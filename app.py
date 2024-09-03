from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from config import NEXTCLOUD_URL, NEXTCLOUD_USER, NEXTCLOUD_PASS, DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
from db_utils import criar_banco_e_tabela, cadastrar_usuario_admin, cadastrar_equipamento, verificar_senha, listar_equipamentos
from mikrotik_utils import conectar_mikrotik, obter_identidade_mikrotik, criar_backup, aguardar_backup, baixar_backup, excluir_backup_mikrotik
from nextcloud_utils import enviar_para_nextcloud
from backup_utils import gerar_nome_arquivo_backup
import logging
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'uma_chave_secreta_aleatoria')

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Chame a função para criar o banco e a tabela
criar_banco_e_tabela()

# Chame a função para criar o usuário admin
cadastrar_usuario_admin()

def verificar_autenticacao():
    """Verifica se o usuário está autenticado."""
    if 'username' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para o login do usuário."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if verificar_senha(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        return render_template('login.html', error='Credenciais inválidas.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Rota para o logout do usuário."""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def home():
    """Rota para a página principal do aplicativo."""
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        ip = request.form.get('ip')
        port = request.form.get('port')
        username = request.form.get('username')
        password = request.form.get('password')
        empresa = request.form.get('empresa')
        marca = request.form.get('marca')

        if not all([ip, port, username, password, empresa, marca]):
            return jsonify({'error': 'Dados ausentes'}), 400

        client = conectar_mikrotik(ip, int(port), username, password)
        if isinstance(client, str):
            return jsonify({'error': client}), 500

        identidade = obter_identidade_mikrotik(client)
        nome_backup = gerar_nome_arquivo_backup(identidade)

        cadastrar_equipamento(ip, int(port), username, password, identidade, empresa, marca)
        criar_backup(client, nome_backup)
        aguardar_backup(client, nome_backup)
        baixar_backup(client, nome_backup)

        caminho_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{nome_backup}.rsc")
        enviar_para_nextcloud(caminho_local, empresa, marca, identidade)

        excluir_backup_mikrotik(client, nome_backup)

        client.close()
        return jsonify({'message': 'Backup realizado e enviado com sucesso!'})

    # Buscar equipamentos cadastrados
    equipamentos = listar_equipamentos()

    # Para requisições GET, renderize a página inicial com os equipamentos
    return render_template('index.html', equipamentos=equipamentos)

if __name__ == '__main__':
    app.run(debug=False)  # Mude para False em produção
