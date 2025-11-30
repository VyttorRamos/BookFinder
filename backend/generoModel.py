import mysql.connector
from configDB import DBConexao

def ListarGeneros():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM categorias WHERE status_categoria = 'ativo' ORDER BY nome"
        cursor.execute(sql)
        generos = cursor.fetchall()
        return True, generos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar categorias: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarGenero(nome_genero, descricao=None):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categorias (nome, descricao) VALUES (%s, %s)", 
                      (nome_genero, descricao))
        conn.commit()
        return True, "Categoria cadastrada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar categoria: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaGeneroPorId(id_genero):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categorias WHERE id_categoria = %s", (id_genero,))
        genero = cursor.fetchone()
        if not genero:
            return False, "Categoria não encontrada."
        return True, genero
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar categoria: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarGenero(id_genero, nome_genero, descricao=None):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        if descricao:
            cursor.execute("UPDATE categorias SET nome = %s, descricao = %s WHERE id_categoria = %s", 
                          (nome_genero, descricao, id_genero))
        else:
            cursor.execute("UPDATE categorias SET nome = %s WHERE id_categoria = %s", 
                          (nome_genero, id_genero))
        conn.commit()
        return True, "Categoria atualizada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar categoria: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DeletarGenero(id_categoria):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # Em vez de excluir, vamos inativar
        sql = "UPDATE categorias SET status_categoria = 'inativo' WHERE id_categoria = %s"
        cursor.execute(sql, (id_categoria,))
        conn.commit()
        return True, "Categoria inativada com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao inativar categoria: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()