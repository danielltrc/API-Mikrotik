import os
import requests
import logging
from config import NEXTCLOUD_URL, NEXTCLOUD_USER, NEXTCLOUD_PASS

def verificar_pasta_no_nextcloud(caminho_pasta):
    """
    Verifica se a pasta existe no Nextcloud.
    """
    try:
        response = requests.request('PROPFIND', os.path.join(NEXTCLOUD_URL, caminho_pasta), auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS))
        print(f"Verificando pasta: {caminho_pasta}")
        print(f"Status code de verificação: {response.status_code}")
        if response.status_code == 207:
            print(f"A pasta já existe no Nextcloud: {caminho_pasta}")
            return True
        elif response.status_code == 404:
            print(f"Pasta não encontrada, será criada: {caminho_pasta}")
            return False
        else:
            print(f"Erro ao verificar a existência da pasta no Nextcloud. Status code: {response.status_code}")
            print(f"Conteúdo do response: {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao verificar a existência da pasta no Nextcloud: {e}")
        return False
    
def criar_pasta_no_nextcloud(caminho_pasta):
    """
    Cria a pasta no Nextcloud se ainda não existir.
    """
    if not verificar_pasta_no_nextcloud(caminho_pasta):
        # Divide o caminho em partes para criar as pastas intermediárias
        partes = caminho_pasta.strip('/').split('/')
        caminho_atual = ''
        for parte in partes:
            caminho_atual = os.path.join(caminho_atual, parte)
            caminho_atual = caminho_atual.replace('\\', '/')  # Substituir barras invertidas por barras normais
            if not verificar_pasta_no_nextcloud(caminho_atual):
                try:
                    response = requests.request('MKCOL', os.path.join(NEXTCLOUD_URL, caminho_atual), auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS))
                    print(f"Criando pasta: {caminho_atual}")
                    print(f"Status code de criação: {response.status_code}")
                    if response.status_code == 201:
                        print(f"Pasta criada no Nextcloud: {caminho_atual}")
                    elif response.status_code == 409:
                        print(f"Conflito ao criar a pasta no Nextcloud. A pasta pode já existir ou há outro problema: {caminho_atual}")
                    else:
                        print(f"Erro ao criar a pasta no Nextcloud. Status code: {response.status_code}")
                        print(f"Conteúdo do response: {response.text}")
                except Exception as e:
                    print(f"Erro ao criar a pasta no Nextcloud: {e}")

def enviar_para_nextcloud(caminho_local, empresa, marca, identidade):
    """
    Envia o arquivo de backup para o Nextcloud via WebDAV.
    """
    try:
        # Criar a estrutura de pasta completa com base nas informações fornecidas
        caminho_pasta = f"BACKUP-RB/{empresa}/{marca}/{identidade}/"
        criar_pasta_no_nextcloud(caminho_pasta)
        with open(caminho_local, 'rb') as f:
            response = requests.put(
                os.path.join(NEXTCLOUD_URL, caminho_pasta + os.path.basename(caminho_local)),
                data=f,
                auth=(NEXTCLOUD_USER, NEXTCLOUD_PASS)
            )
            print(f"Enviando arquivo para: {caminho_pasta + os.path.basename(caminho_local)}")
            print(f"Status code de envio: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"Arquivo enviado para o Nextcloud com sucesso: {os.path.basename(caminho_local)}")
            else:
                print(f"Erro ao enviar arquivo para o Nextcloud. Status code: {response.status_code}")
                print(f"Conteúdo do response: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar arquivo para o Nextcloud: {e}")
