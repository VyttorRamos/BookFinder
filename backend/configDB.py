import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

def DBConexao(): # abre e retorna uma conexão com o MySQL
    try:
        print("[db_config] Tentando conectar com:", MYSQL_HOST, MYSQL_USER, MYSQL_DB, MYSQL_PORT)
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT
        )
        print("[db_config] Conexão criada, is_connected():", conn.is_connected())
        return conn
    except Exception as e:
        print("[db_config] ERRO ao conectar:", repr(e))
        return None