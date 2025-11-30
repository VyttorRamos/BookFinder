import mysql.connector
from configDB import DBConexao

def ListarLivros():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT l.*, e.nome as editora_nome, c.nome as categoria_nome 
            FROM livros l 
            LEFT JOIN editoras e ON l.id_editora = e.id_editora 
            LEFT JOIN categorias c ON l.id_categoria = c.id_categoria 
            WHERE l.status_livro = 'ativo'
            ORDER BY l.titulo
        """
        cursor.execute(sql)
        livros = cursor.fetchall()
        return True, livros
    except mysql.connector.Error as err:
        return False, f"Erro ao listar livros: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarLivro(titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None, capa=None, quantidade_total=1):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, isbn, ano_publicacao, id_editora, id_categoria, capa, quantidade_total, quantidade_disponivel) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, isbn, ano_publicacao, id_editora, id_categoria, capa, quantidade_total, quantidade_total))
        
        livro_id = cursor.lastrowid
        
        # Criar cópias do livro
        for i in range(quantidade_total):
            cod_interno = f"{livro_id}-{i+1}"
            cursor.execute("""
                INSERT INTO copias (id_livro, cod_interno, status_copia)
                VALUES (%s, %s, 'disponivel')
            """, (livro_id, cod_interno))
        
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

def AtualizarLivro(id_livro, titulo, isbn=None, ano_publicacao=None, id_editora=None, id_categoria=None, capa=None, quantidade_total=None):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        # Buscar livro atual para manter a quantidade disponível correta
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT quantidade_total, quantidade_disponivel FROM livros WHERE id_livro = %s", (id_livro,))
        livro_atual = cursor.fetchone()
        
        if not livro_atual:
            return False, "Livro não encontrado."
        
        # Calcular nova quantidade disponível se a quantidade total mudar
        if quantidade_total is not None:
            diferenca = quantidade_total - livro_atual['quantidade_total']
            nova_quantidade_disponivel = livro_atual['quantidade_disponivel'] + diferenca
        else:
            quantidade_total = livro_atual['quantidade_total']
            nova_quantidade_disponivel = livro_atual['quantidade_disponivel']
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE livros 
            SET titulo = %s, isbn = %s, ano_publicacao = %s, id_editora = %s, 
                id_categoria = %s, capa = %s, quantidade_total = %s, quantidade_disponivel = %s
            WHERE id_livro = %s
        """, (titulo, isbn, ano_publicacao, id_editora, id_categoria, capa, quantidade_total, nova_quantidade_disponivel, id_livro))
        
        # Atualizar cópias se a quantidade total mudou
        if quantidade_total is not None:
            # Contar cópias existentes
            cursor.execute("SELECT COUNT(*) as total_copias FROM copias WHERE id_livro = %s", (id_livro,))
            total_copias = cursor.fetchone()['total_copias']
            
            if quantidade_total > total_copias:
                # Adicionar novas cópias
                for i in range(total_copias + 1, quantidade_total + 1):
                    cod_interno = f"{id_livro}-{i}"
                    cursor.execute("""
                        INSERT INTO copias (id_livro, cod_interno, status_copia)
                        VALUES (%s, %s, 'disponivel')
                    """, (id_livro, cod_interno))
            elif quantidade_total < total_copias:
                # Remover cópias extras (apenas as disponíveis)
                cursor.execute("""
                    DELETE FROM copias 
                    WHERE id_livro = %s AND status_copia = 'disponivel'
                    LIMIT %s
                """, (id_livro, total_copias - quantidade_total))
        
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
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # Em vez de excluir, vamos inativar (usando 'removido' do enum existente)
        sql = "UPDATE livros SET status_livro = 'removido' WHERE id_livro = %s"
        cursor.execute(sql, (id_livro,))
        conn.commit()
        return True, "Livro inativado com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao inativar livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def VerificarDisponibilidade(id_livro):
    """Verifica se o livro está disponível para empréstimo"""
    conn = None
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as copias_disponiveis 
            FROM copias 
            WHERE id_livro = %s AND status_copia = 'disponivel'
        """, (id_livro,))
        resultado = cursor.fetchone()
        
        disponivel = resultado['copias_disponiveis'] > 0
        return True, disponivel
    except Exception as e:
        return False, f"Erro ao verificar disponibilidade: {str(e)}"
    finally:
        if conn and conn.is_connected():
            conn.close()