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
            ORDER BY l.titulo
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

def CadastrarLivro(titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None, capa=None):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, isbn, ano_publicacao, id_editora, id_categoria, capa) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (titulo, isbn, ano_publicacao, id_editora, id_categoria, capa))
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

def AtualizarLivro(id_livro, titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None, capa=None):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        # Construir a query dinamicamente baseado nos campos fornecidos
        campos = []
        valores = []
        
        campos.append("titulo = %s")
        valores.append(titulo)
        
        if isbn is not None:
            campos.append("isbn = %s")
            valores.append(isbn)
            
        if ano_publicacao is not None:
            campos.append("ano_publicacao = %s")
            valores.append(ano_publicacao)
            
        if id_editora is not None:
            campos.append("id_editora = %s")
            valores.append(id_editora)
            
        if id_categoria is not None:
            campos.append("id_categoria = %s")
            valores.append(id_categoria)
            
        if capa is not None:
            campos.append("capa = %s")
            valores.append(capa)
        
        valores.append(id_livro)
        
        query = f"UPDATE livros SET {', '.join(campos)} WHERE id_livro = %s"
        
        cursor = conn.cursor()
        cursor.execute(query, valores)
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