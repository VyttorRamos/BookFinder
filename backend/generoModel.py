import mysql.connector
from db_connection import get_db_connection

class Genero:
    def __init__(self, id_genero=None, nome_genero=None):
        self.id_genero = id_genero
        self.nome_genero = nome_genero

class GeneroDAO:
    @staticmethod
    def listar():
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM generos")
                    return True, [Genero(**dados) for dados in cursor.fetchall()]
        except mysql.connector.Error as err:
            return False, f"Erro ao listar gêneros: {err}"

    @staticmethod
    def cadastrar(genero):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO generos (nome_genero) VALUES (%s)",
                        (genero.nome_genero,)
                    )
                    conn.commit()
                    return True, "Gênero cadastrado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao cadastrar gênero: {err}"

    @staticmethod
    def buscar_por_id(id_genero):
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT * FROM generos WHERE id_genero = %s",
                        (id_genero,)
                    )
                    resultado = cursor.fetchone()
                    if not resultado:
                        return False, "Gênero não encontrado."
                    return True, Genero(**resultado)
        except mysql.connector.Error as err:
            return False, f"Erro ao buscar gênero: {err}"

    @staticmethod
    def atualizar(genero):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE generos SET nome_genero = %s WHERE id_genero = %s",
                        (genero.nome_genero, genero.id_genero)
                    )
                    conn.commit()
                    return True, "Gênero atualizado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao atualizar gênero: {err}"

    @staticmethod
    def deletar(id_genero):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Verificar se o gênero está sendo usado em algum livro
                    cursor.execute(
                        "SELECT * FROM livros WHERE genero_id = %s",
                        (id_genero,)
                    )
                    if cursor.fetchone():
                        return False, "Não é possível excluir o gênero, pois ele está associado a livros existentes."

                    cursor.execute(
                        "DELETE FROM generos WHERE id_genero = %s",
                        (id_genero,)
                    )
                    conn.commit()
                    return True, "Gênero deletado com sucesso!"
        except mysql.connector.Error as err:
            return False, f"Erro ao deletar gênero: {err}"