import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL')
NEXTCLOUD_USER = os.getenv('NEXTCLOUD_USER')
NEXTCLOUD_PASS = os.getenv('NEXTCLOUD_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
