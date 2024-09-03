import mysql.connector
from mysql.connector import Error
import logging
import bcrypt
from contextlib import contextmanager
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@contextmanager
def get_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        yield connection
    except Error as e:
        logging.error(f"Database error: {e}")
        raise  # Re-raise the exception to let the caller handle it
    finally:
        if connection and connection.is_connected():
            connection.close()


def criar_banco_e_tabela():
    try:
        with mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_DATABASE}`")
                cursor.execute(f"USE `{DB_DATABASE}`")

                create_equipamentos_table_query = """
                CREATE TABLE IF NOT EXISTS equipamentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(15) NOT NULL,
                    port INT NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    empresa VARCHAR(255) NOT NULL,
                    marca VARCHAR(255) NOT NULL,
                    identity VARCHAR(255) NOT NULL
                )
                """
                cursor.execute(create_equipamentos_table_query)

                create_users_table_query = """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
                """
                cursor.execute(create_users_table_query)

                connection.commit()
                logging.info("Banco de dados e tabelas criados com sucesso.")
    except Error as e:
        logging.error(f"Erro ao criar o banco de dados ou tabelas: {e}")

def cadastrar_usuario_admin():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                username = 'admin'
                password = '123456'
                hashed_password = hash_password(password)

                query = """INSERT IGNORE INTO usuarios (username, password) VALUES (%s, %s)"""
                cursor.execute(query, (username, hashed_password))
                connection.commit()

                # Verificar se o usuário foi realmente inserido
                cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
                result = cursor.fetchone()
                if result:
                    ''
                else:
                    logging.warning("Usuário admin não foi inserido.")

    except Error as e:
        logging.error(f"Erro ao cadastrar o usuário admin: {e}")


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

import bcrypt

def check_password(hashed_password, password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def cadastrar_equipamento(ip, port, username, password, identity, marca, empresa):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                hashed_password = hash_password(password)
                query = """INSERT INTO equipamentos (ip, port, username, password, identity, marca, empresa)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                values = (ip, port, username, hashed_password, identity, marca, empresa)
                cursor.execute(query, values)
                connection.commit()
                logging.info("Equipamento cadastrado com sucesso.")
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados MySQL: {e}")


def verificar_senha(username, senha_fornecida):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                query = """SELECT password FROM usuarios WHERE username = %s"""
                cursor.execute(query, (username,))
                stored_hash = cursor.fetchone()
                if stored_hash:
                    return check_password(stored_hash[0], senha_fornecida)
                return False
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return False



def listar_equipamentos():
    try:
        with get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT ip, port, username, identity FROM equipamentos"
                cursor.execute(query)
                return cursor.fetchall()
    except Error as e:
        logging.error(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return []


if __name__ == '__main__':
    criar_banco_e_tabela()
    cadastrar_usuario_admin()
