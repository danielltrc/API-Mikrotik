import paramiko
import time
import logging
import os

def conectar_mikrotik(ip, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=port, username=username, password=password)
        return client
    except paramiko.ssh_exception.SSHException as e:
        return str(e)

def obter_identidade_mikrotik(client):
    try:
        stdin, stdout, stderr = client.exec_command("/system identity print")
        output = stdout.read().decode('utf-8')
        return output.split("name: ")[1].strip()
    except Exception as e:
        logging.error(f"Erro ao obter a identidade do MikroTik: {e}")
        return "default"

def criar_backup(client, nome_backup):
    try:
        client.exec_command(f"export file={nome_backup}")
        logging.info("Comando de backup enviado ao MikroTik.")
    except Exception as e:
        logging.error(f"Erro ao criar backup no MikroTik: {e}")

def aguardar_backup(client, nome_backup):
    for _ in range(12):  # Tentativas limitadas
        time.sleep(5)
        try:
            stdin, stdout, stderr = client.exec_command(f"/file print where name={nome_backup}.rsc")
            output = stdout.read().decode('utf-8')
            if nome_backup in output:
                logging.info("Backup gerado e disponível no MikroTik.")
                return
        except Exception as e:
            logging.error(f"Erro ao verificar o arquivo de backup no MikroTik: {e}")
    logging.error("O arquivo de backup não está disponível ainda.")

def baixar_backup(client, nome_backup):
    try:
        sftp = client.open_sftp()
        caminho_remoto = f"/{nome_backup}.rsc"
        caminho_local = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{nome_backup}.rsc")

        if f"{nome_backup}.rsc" in sftp.listdir('/'):
            sftp.get(caminho_remoto, caminho_local)
            logging.info(f"Backup baixado para o servidor local em {caminho_local}.")
        else:
            logging.error(f"Arquivo {nome_backup}.rsc não encontrado no MikroTik.")

        sftp.close()
    except Exception as e:
        logging.error(f"Erro ao baixar o backup do MikroTik: {e}")

def excluir_backup_mikrotik(client, nome_backup):
    try:
        client.exec_command(f"/file remove {nome_backup}.rsc")
        logging.info("Backup excluído do MikroTik.")
    except Exception as e:
        logging.error(f"Erro ao excluir o backup do MikroTik: {e}")
