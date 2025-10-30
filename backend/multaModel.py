import mysql.connector
from configDB import DBConexao


def ListarMultas():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        # Join para pegar nome do usuário
        sql = """
            SELECT 
                m.id_multa, 
                u.nome_completo, 
                m.valor_multa, 
                m.data_multa,
                m.paga
            FROM multas m
            JOIN usuarios u ON m.id_usuario = u.id_usuario
        """
        cursor.execute(sql)
        multas = cursor.fetchall()
        return True, multas
    except mysql.connector.Error as err:
        return False, f"Erro ao listar multas: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaMultaPorId(id_multa):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """SELECT m.*, u.nome_completo FROM multas m
                 JOIN usuarios u ON m.id_usuario = u.id_usuario
                 WHERE m.id_multa = %s"""
        cursor.execute(sql, (id_multa,))
        multa = cursor.fetchone()
        if not multa:
            return False, "Multa não encontrada."
        return True, multa
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar multa: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def RemoverMulta(id_multa):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # A "remoção" na verdade é marcar a multa como paga
        cursor.execute("UPDATE multas SET paga = TRUE WHERE id_multa = %s", (id_multa,))
        conn.commit()
        return True, "Multa removida (paga) com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao remover multa: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
