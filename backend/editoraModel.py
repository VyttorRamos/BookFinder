import mysql.connector
from configDB import DBConexao
from datetime import datetime

def ListarEditoras():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM editoras WHERE status_editora = 'ativo' ORDER BY nome"
        cursor.execute(sql)
        editoras = cursor.fetchall()
        return True, editoras
    except mysql.connector.Error as err:
        return False, f"Erro ao listar editoras: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarEditora(nome, endereco=None, telefone=None, email=None):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        sql = "INSERT INTO editoras (nome, endereco, telefone, email, status_editora) VALUES (%s, %s, %s, %s, 'ativo')"
        cursor.execute(sql, (nome, endereco, telefone, email))
        conn.commit()
        return True, "Editora cadastrada com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao cadastrar editora: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaEditoraPorId(id_editora):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM editoras WHERE id_editora = %s"
        cursor.execute(sql, (id_editora,))
        editora = cursor.fetchone()
        if not editora:
            return False, "Editora não encontrada."
        return True, editora
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar editora: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarEditora(id_editora, nome, endereco=None, telefone=None, email=None):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        sql = "UPDATE editoras SET nome = %s, endereco = %s, telefone = %s, email = %s WHERE id_editora = %s"
        cursor.execute(sql, (nome, endereco, telefone, email, id_editora))
        conn.commit()
        return True, "Editora atualizada com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao atualizar editora: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DeletarEditora(id_editora):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # Em vez de excluir, vamos inativar
        sql = "UPDATE editoras SET status_editora = 'inativo' WHERE id_editora = %s"
        cursor.execute(sql, (id_editora,))
        conn.commit()
        return True, "Editora inativada com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao inativar editora: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()