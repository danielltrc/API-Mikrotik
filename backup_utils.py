from datetime import datetime
import os

def gerar_nome_arquivo_backup(identidade):
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    return f"{identidade}_{timestamp}"
