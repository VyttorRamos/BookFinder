import mysql.connector
from configDB import DBConexao


def ListarLivros():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM livros")
        livros = cursor.fetchall()
        return True, livros
    except mysql.connector.Error as err:
        return False, f"Erro ao listar livros: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarLivro(titulo, autor, ano, genero_id):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, genero_id, disponivel) VALUES (%s, %s, %s, %s, TRUE)", (titulo, autor, ano, genero_id))
        conn.commit()
        return True, "Livro cadastrado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaLivroPorId(id_livro):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM livros WHERE id_livro = %s", (id_livro,))
        livro = cursor.fetchone()
        if not livro:
            return False, "Livro não encontrado."
        return True, livro
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarLivro(id_livro, titulo, autor, ano, genero_id):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE livros SET titulo = %s, autor = %s, ano_publicacao = %s, genero_id = %s WHERE id_livro = %s", (titulo, autor, ano, genero_id, id_livro))
        conn.commit()
        return True, "Livro atualizado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DeletarLivro(id_livro):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # Verificar se o livro está em algum empréstimo ativo
        cursor.execute("SELECT * FROM emprestimos WHERE id_livro = %s AND data_devolucao IS NULL", (id_livro,))
        if cursor.fetchone():
            return False, "Não é possível excluir o livro, pois ele está emprestado."
        
        cursor.execute("DELETE FROM livros WHERE id_livro = %s", (id_livro,))
        conn.commit()
        return True, "Livro deletado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao deletar livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
