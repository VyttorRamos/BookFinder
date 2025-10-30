import mysql.connector
from db_connection import get_db_connection

class Livro:
    def __init__(self, id_livro=None, titulo=None, autor=None, ano_publicacao=None, genero_id=None, disponivel=True):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao
        self.genero_id = genero_id
        self.disponivel = disponivel

    def __str__(self):
        return f"Livro(id={self.id_livro}, titulo='{self.titulo}', autor='{self.autor}')"

class LivroDAO:
    @staticmethod
    def listar():
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM livros")
                    return True, [Livro(**dados) for dados in cursor.fetchall()]
        except mysql.connector.Error as err:
            return False, f"Erro ao listar livros: {err}"

    @staticmethod
    def cadastrar(livro):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO livros (titulo, autor, ano_publicacao, genero_id, disponivel) VALUES (%s, %s, %s, %s, %s)",
                        (livro.titulo, livro.autor, livro.ano_publicacao, livro.genero_id, livro.disponivel)
                    )
                    conn.commit()
                    return True, "Livro cadastrado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao cadastrar livro: {err}"

    @staticmethod
    def buscar_por_id(id_livro):
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT * FROM livros WHERE id_livro = %s",
                        (id_livro,)
                    )
                    resultado = cursor.fetchone()
                    if not resultado:
                        return False, "Livro não encontrado."
                    return True, Livro(**resultado)
        except mysql.connector.Error as err:
            return False, f"Erro ao buscar livro: {err}"

    @staticmethod
    def atualizar(livro):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE livros SET titulo = %s, autor = %s, ano_publicacao = %s, genero_id = %s WHERE id_livro = %s",
                        (livro.titulo, livro.autor, livro.ano_publicacao, livro.genero_id, livro.id_livro)
                    )
                    conn.commit()
                    return True, "Livro atualizado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao atualizar livro: {err}"

    @staticmethod
    def deletar(id_livro):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Verificar se o livro está em algum empréstimo ativo
                    cursor.execute(
                        "SELECT * FROM emprestimos WHERE id_livro = %s AND data_devolucao IS NULL",
                        (id_livro,)
                    )
                    if cursor.fetchone():
                        return False, "Não é possível excluir o livro, pois ele está emprestado."
                    
                    cursor.execute(
                        "DELETE FROM livros WHERE id_livro = %s",
                        (id_livro,)
                    )
                    conn.commit()
                    return True, "Livro deletado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao deletar livro: {err}"

    @staticmethod
    def listar_com_generos():
        """Método adicional para listar livros com informações do gênero"""
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    query = """
                        SELECT l.*, g.nome_genero 
                        FROM livros l 
                        LEFT JOIN generos g ON l.genero_id = g.id_genero
                    """
                    cursor.execute(query)
                    return True, cursor.fetchall()
        except mysql.connector.Error as err:
            return False, f"Erro ao listar livros com gêneros: {err}"

    @staticmethod
    def buscar_por_genero(genero_id):
        """Método adicional para buscar livros por gênero"""
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT * FROM livros WHERE genero_id = %s",
                        (genero_id,)
                    )
                    return True, [Livro(**dados) for dados in cursor.fetchall()]
        except mysql.connector.Error as err:
            return False, f"Erro ao buscar livros por gênero: {err}"

    @staticmethod
    def atualizar_disponibilidade(id_livro, disponivel):
        """Método adicional para atualizar a disponibilidade do livro"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE livros SET disponivel = %s WHERE id_livro = %s",
                        (disponivel, id_livro)
                    )
                    conn.commit()
                    return True, "Disponibilidade do livro atualizada com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao atualizar disponibilidade: {err}"