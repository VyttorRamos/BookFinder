import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()

# CORREÇÃO: Use DB_ em vez de MYSQL_
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "BookFinderDB")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

def DBConexao():
    try:
        print(f"[db_config] Tentando conectar com:")
        print(f"  Host: {DB_HOST}")
        print(f"  User: {DB_USER}")
        print(f"  Database: {DB_NAME}")
        print(f"  Port: {DB_PORT}")
        print(f"  Password: {'***' if DB_PASSWORD else 'None'}")
        
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
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