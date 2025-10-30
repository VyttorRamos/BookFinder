from configDB import DBConexao
from mysql.connector import Error

def CadastroLivro(titulo, autor, ano, genero_id):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor()
        sql = "INSERT INTO livros (titulo, autor, ano_publicacao, genero_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (titulo, autor, ano, genero_id))
        conn.commit()
        livro_id = cursor.lastrowid
        cursor.close()
        return True, livro_id
    except Exception as e:
        print(f"[CadastroLivro] ERRO: {e}")
        return False, "Erro ao cadastrar livro"
    finally:
        if conn and conn.is_connected():
            conn.close()

def ListarLivros():
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor(dictionary=True)
        sql = "SELECT l.id_livro, l.titulo, l.autor, l.ano_publicacao, g.nome_genero FROM livros l JOIN generos g ON l.genero_id = g.id_genero"
        cursor.execute(sql)
        livros = cursor.fetchall()
        cursor.close()
        return True, livros
    except Exception as e:
        print(f"[ListarLivros] ERRO: {e}")
        return False, "Erro ao listar livros"
    finally:
        if conn and conn.is_connected():
            conn.close()

def PegaLivroPorId(id_livro):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor(dictionary=True)
        sql = "SELECT id_livro, titulo, autor, ano_publicacao, genero_id FROM livros WHERE id_livro = %s"
        cursor.execute(sql, (id_livro,))
        livro = cursor.fetchone()
        cursor.close()
        if not livro:
            return False, "Livro não encontrado"
        return True, livro
    except Exception as e:
        print(f"[PegaLivroPorId] ERRO: {e}")
        return False, "Erro ao buscar livro"
    finally:
        if conn and conn.is_connected():
            conn.close()

def AtualizarLivro(id_livro, titulo, autor, ano, genero_id):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor()
        sql = "UPDATE livros SET titulo = %s, autor = %s, ano_publicacao = %s, genero_id = %s WHERE id_livro = %s"
        cursor.execute(sql, (titulo, autor, ano, genero_id, id_livro))
        conn.commit()
        cursor.close()
        return True, "Livro atualizado com sucesso"
    except Exception as e:
        print(f"[AtualizarLivro] ERRO: {e}")
        return False, "Erro ao atualizar livro"
    finally:
        if conn and conn.is_connected():
            conn.close()

def DeletarLivro(id_livro):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor()
        sql = "DELETE FROM livros WHERE id_livro = %s"
        cursor.execute(sql, (id_livro,))
        conn.commit()
        cursor.close()
        return True, "Livro deletado com sucesso"
    except Exception as e:
        print(f"[DeletarLivro] ERRO: {e}")
        return False, "Erro ao deletar livro"
    finally:
        if conn and conn.is_connected():
            conn.close()
