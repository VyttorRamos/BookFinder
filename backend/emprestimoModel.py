import mysql.connector
from db_connection import get_db_connection
from datetime import date, timedelta

def ListarEmprestimos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Join para pegar nomes de livros e usuários
        sql = """
            SELECT 
                e.id_emprestimo, 
                l.titulo, 
                u.nome_completo, 
                e.data_emprestimo, 
                e.data_devolucao 
            FROM emprestimos e
            JOIN livros l ON e.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.data_devolucao IS NULL
        """
        cursor.execute(sql)
        emprestimos = cursor.fetchall()
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def RealizarEmprestimo(id_livro, id_usuario):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verificar se o livro está disponível
        cursor.execute("SELECT disponivel FROM livros WHERE id_livro = %s", (id_livro,))
        livro = cursor.fetchone()
        if not livro or not livro[0]:
            return False, "Livro não está disponível para empréstimo."

        # 2. Verificar se o usuário tem multas pendentes
        cursor.execute("SELECT * FROM multas WHERE id_usuario = %s AND paga = FALSE", (id_usuario,))
        if cursor.fetchone():
            return False, "Usuário possui multas pendentes e não pode realizar empréstimos."

        # 3. Realizar o empréstimo
        data_emprestimo = date.today()
        data_devolucao_prevista = data_emprestimo + timedelta(days=14) # Prazo de 14 dias
        cursor.execute("INSERT INTO emprestimos (id_livro, id_usuario, data_emprestimo, data_devolucao) VALUES (%s, %s, %s, %s)", 
                       (id_livro, id_usuario, data_emprestimo, data_devolucao_prevista))
        
        # 4. Atualizar o status do livro para indisponível
        cursor.execute("UPDATE livros SET disponivel = FALSE WHERE id_livro = %s", (id_livro,))
        
        conn.commit()
        return True, "Empréstimo realizado com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao realizar empréstimo: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaEmprestimoPorId(id_emprestimo):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """SELECT e.*, l.titulo, u.nome_completo FROM emprestimos e 
                 JOIN livros l ON e.id_livro = l.id_livro
                 JOIN usuarios u ON e.id_usuario = u.id_usuario
                 WHERE e.id_emprestimo = %s"""
        cursor.execute(sql, (id_emprestimo,))
        emprestimo = cursor.fetchone()
        if not emprestimo:
            return False, "Empréstimo não encontrado."
        return True, emprestimo
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar empréstimo: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def RenovarEmprestimo(id_emprestimo):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Adicionar mais 14 dias à data de devolução
        cursor.execute("UPDATE emprestimos SET data_devolucao = data_devolucao + INTERVAL 14 DAY WHERE id_emprestimo = %s", (id_emprestimo,))
        conn.commit()
        return True, "Empréstimo renovado com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao renovar empréstimo: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DevolverLivro(id_emprestimo):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Pegar dados do empréstimo
        cursor.execute("SELECT * FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
        emprestimo = cursor.fetchone()
        if not emprestimo:
            return False, "Empréstimo não encontrado."

        id_livro = emprestimo['id_livro']
        id_usuario = emprestimo['id_usuario']
        data_devolucao_prevista = emprestimo['data_devolucao']

        # 2. Atualizar a data de devolução para a data atual
        data_devolucao_real = date.today()
        cursor.execute("UPDATE emprestimos SET data_devolucao = %s WHERE id_emprestimo = %s", (data_devolucao_real, id_emprestimo))

        # 3. Atualizar status do livro para disponível
        cursor.execute("UPDATE livros SET disponivel = TRUE WHERE id_livro = %s", (id_livro,))

        # 4. Verificar se há multa
        if data_devolucao_real > data_devolucao_prevista:
            dias_atraso = (data_devolucao_real - data_devolucao_prevista).days
            valor_multa = dias_atraso * 1.50 # R$ 1,50 por dia de atraso
            cursor.execute("INSERT INTO multas (id_emprestimo, id_usuario, valor_multa, data_multa) VALUES (%s, %s, %s, %s)",
                           (id_emprestimo, id_usuario, valor_multa, data_devolucao_real))

        conn.commit()
        return True, "Livro devolvido com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao devolver livro: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarAtrasados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        today = date.today()
        sql = """
            SELECT 
                e.id_emprestimo, 
                l.titulo, 
                u.nome_completo, 
                e.data_emprestimo, 
                e.data_devolucao
            FROM emprestimos e
            JOIN livros l ON e.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.data_devolucao < %s AND e.data_devolucao IS NOT NULL
        """
        cursor.execute(sql, (today,))
        emprestimos = cursor.fetchall()
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos atrasados: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
