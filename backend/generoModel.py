import mysql.connector
from db_connection import get_db_connection

def ListarGeneros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM generos")
        generos = cursor.fetchall()
        return True, generos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar gêneros: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarGenero(nome_genero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO generos (nome_genero) VALUES (%s)", (nome_genero,))
        conn.commit()
        return True, "Gênero cadastrado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar gênero: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaGeneroPorId(id_genero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM generos WHERE id_genero = %s", (id_genero,))
        genero = cursor.fetchone()
        if not genero:
            return False, "Gênero não encontrado."
        return True, genero
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar gênero: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarGenero(id_genero, nome_genero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE generos SET nome_genero = %s WHERE id_genero = %s", (nome_genero, id_genero))
        conn.commit()
        return True, "Gênero atualizado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar gênero: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DeletarGenero(id_genero):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verificar se o gênero está sendo usado em algum livro
        cursor.execute("SELECT * FROM livros WHERE genero_id = %s", (id_genero,))
        if cursor.fetchone():
            return False, "Não é possível excluir o gênero, pois ele está associado a livros existentes."

        cursor.execute("DELETE FROM generos WHERE id_genero = %s", (id_genero,))
        conn.commit()
        return True, "Gênero deletado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao deletar gênero: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
