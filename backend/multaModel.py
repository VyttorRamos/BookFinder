import mysql.connector
from configDB import DBConexao

def ListarMultas():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                m.id_multa,
                m.valor,
                m.status_multa,
                m.dt_criacao,
                m.dt_pagamento,
                e.id_emprestimo,
                l.titulo,
                u.nome_completo
            FROM multas m
            JOIN emprestimos e ON m.id_emprestimo = e.id_emprestimo
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            ORDER BY m.dt_criacao DESC
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
        sql = """
            SELECT 
                m.*,
                e.id_emprestimo,
                l.titulo,
                u.nome_completo,
                u.id_usuario
            FROM multas m
            JOIN emprestimos e ON m.id_emprestimo = e.id_emprestimo
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE m.id_multa = %s
        """
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
        
        # Atualizar o status da multa para 'cancelado' em vez de deletar
        cursor.execute("""
            UPDATE multas 
            SET status_multa = 'cancelado', dt_pagamento = NOW() 
            WHERE id_multa = %s
        """, (id_multa,))
        
        conn.commit()
        return True, "Multa removida/cancelada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao remover multa: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarMultasPorUsuario(id_usuario):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT m.id_multa, l.titulo, m.valor, m.status_multa
            FROM multas m
            JOIN emprestimos e ON m.id_emprestimo = e.id_emprestimo
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            WHERE e.id_usuario = %s AND m.status_multa = 'pendente'
        """
        cursor.execute(sql, (id_usuario,))
        multas = cursor.fetchall()
        cursor.close()
        return True, multas
    except Exception as e:
        print(f"[ListarMultasPorUsuario] ERRO: {e}")
        return False, "Erro ao buscar multas do usuário"
    finally:
        if conn and conn.is_connected():
            conn.close()