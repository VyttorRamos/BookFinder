import mysql.connector
from configDB import DBConexao
from datetime import datetime
from emprestimoModel import ObterConfiguracoesEmprestimo

def ListarMultas():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                m.id_multa,
                m.valor,
                m.dias_atraso,
                m.status_multa,
                m.dt_criacao,
                m.dt_pagamento,
                e.id_emprestimo,
                l.titulo,
                u.nome_completo,
                u.id_usuario
            FROM multas m
            JOIN emprestimos e ON m.id_emprestimo = e.id_emprestimo
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON m.id_usuario = u.id_usuario
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
            JOIN usuarios u ON m.id_usuario = u.id_usuario
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
        
        # Verificar se a multa existe
        cursor.execute("SELECT * FROM multas WHERE id_multa = %s", (id_multa,))
        multa = cursor.fetchone()
        
        if not multa:
            return False, "Multa não encontrada."
        
        # Remover a multa
        cursor.execute("DELETE FROM multas WHERE id_multa = %s", (id_multa,))
        
        conn.commit()
        return True, "Multa removida com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao remover multa: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def QuitarMulta(id_multa):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        
        # Verificar se a multa existe
        cursor.execute("SELECT * FROM multas WHERE id_multa = %s", (id_multa,))
        multa = cursor.fetchone()
        
        if not multa:
            return False, "Multa não encontrada."
        
        # Marcar multa como paga
        dt_pagamento = datetime.now()
        cursor.execute("""
            UPDATE multas 
            SET status_multa = 'pago', dt_pagamento = %s 
            WHERE id_multa = %s
        """, (dt_pagamento, id_multa))
        
        conn.commit()
        return True, "Multa quitada com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao quitar multa: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarMultasPorUsuario(id_usuario: int):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                m.id_multa,
                m.valor,
                m.status_multa,
                m.dt_criacao,
                m.dias_atraso,
                l.titulo,
                e.dt_emprestimo
            FROM multas m
            JOIN emprestimos e ON m.id_emprestimo = e.id_emprestimo
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            WHERE m.id_usuario = %s 
            AND m.status_multa = 'pendente'
            ORDER BY m.dt_criacao DESC
        """
        cursor.execute(sql, (id_usuario,))
        multas = cursor.fetchall()
        return True, multas
    except Error as err:
        print(f"[ListarMultasPorUsuario] ERRO: {err}")
        return False, f"Erro ao listar multas: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CalcularMultaAtraso(id_emprestimo):
    """Calcula multa para empréstimo em atraso"""
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        hoje = datetime.now().date()
        
        # Obter configurações do sistema
        config = ObterConfiguracoesEmprestimo()
        
        # Buscar dados do empréstimo
        cursor.execute("""
            SELECT *, DATEDIFF(%s, dt_prevista_devolucao) as dias_atraso
            FROM emprestimos 
            WHERE id_emprestimo = %s
        """, (hoje, id_emprestimo))
        
        emprestimo = cursor.fetchone()
        
        if not emprestimo:
            return False, "Empréstimo não encontrado."
            
        if emprestimo['dias_atraso'] <= 0:
            return False, "Empréstimo não está em atraso."
        
        # Valor da multa baseado na configuração
        valor_multa = emprestimo['dias_atraso'] * config['multa_por_dia']
        
        return True, {
            'dias_atraso': emprestimo['dias_atraso'],
            'valor_multa': valor_multa,
            'data_prevista': emprestimo['dt_prevista_devolucao'],
            'multa_por_dia': config['multa_por_dia']
        }
        
    except Exception as e:
        return False, f"Erro ao calcular multa: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()