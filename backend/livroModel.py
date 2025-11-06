import mysql.connector
from configDB import DBConexao

def ListarLivros():
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.*, c.nome as categoria_nome, e.nome as editora_nome 
            FROM livros l 
            LEFT JOIN categorias c ON l.id_categoria = c.id_categoria 
            LEFT JOIN editoras e ON l.id_editora = e.id_editora
        """)
        livros = cursor.fetchall()
        return True, livros
    except mysql.connector.Error as err:
        return False, f"Erro ao listar livros: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao listar livros: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def CadastrarLivro(titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, isbn, ano_publicacao, id_editora, id_categoria) 
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, isbn, ano_publicacao, id_editora, id_categoria))
        conn.commit()
        return True, "Livro cadastrado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar livro: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao cadastrar livro: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def PegaLivroPorId(id_livro):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.*, c.nome as categoria_nome, e.nome as editora_nome 
            FROM livros l 
            LEFT JOIN categorias c ON l.id_categoria = c.id_categoria 
            LEFT JOIN editoras e ON l.id_editora = e.id_editora 
            WHERE l.id_livro = %s
        """, (id_livro,))
        livro = cursor.fetchone()
        if not livro:
            return False, "Livro não encontrado."
        return True, livro
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar livro: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao buscar livro: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def AtualizarLivro(id_livro, titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE livros 
            SET titulo = %s, isbn = %s, ano_publicacao = %s, id_editora = %s, id_categoria = %s 
            WHERE id_livro = %s
        """, (titulo, isbn, ano_publicacao, id_editora, id_categoria, id_livro))
        conn.commit()
        return True, "Livro atualizado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar livro: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao atualizar livro: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def DeletarLivro(id_livro):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        
        # Verificar se o livro tem cópias ou empréstimos
        cursor.execute("SELECT * FROM copias WHERE id_livro = %s", (id_livro,))
        if cursor.fetchone():
            return False, "Não é possível excluir o livro, pois existem cópias cadastradas."
            
        cursor.execute("DELETE FROM livros WHERE id_livro = %s", (id_livro,))
        conn.commit()
        return True, "Livro deletado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao deletar livro: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao deletar livro: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()