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

def DBConexao():
    try:
        print(f"[db_config] Tentando conectar com:")
        print(f"  Host: {MYSQL_HOST}")
        print(f"  User: {MYSQL_USER}")
        print(f"  Database: {MYSQL_DB}")
        print(f"  Port: {MYSQL_PORT}")
        print(f"  Password: {'***' if MYSQL_PASSWORD else 'None'}")
        
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            connection_timeout=10
        )
        
        if conn.is_connected():
            print("[db_config] ✅ Conexão bem-sucedida!")
            db_info = conn.get_server_info()
            print(f"[db_config] Servidor MySQL versão: {db_info}")
            return conn
        else:
            print("[db_config] ❌ Conexão falhou")
            return None
            
    except Exception as e:
        print(f"[db_config] ❌ ERRO ao conectar: {repr(e)}")
        print(f"[db_config] Tipo do erro: {type(e).__name__}")
        return None