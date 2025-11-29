import mysql.connector
from configDB import DBConexao
from datetime import datetime, timedelta

def ListarEmprestimos():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                e.id_emprestimo, 
                l.titulo, 
                u.nome_completo, 
                e.dt_emprestimo, 
                e.dt_prevista_devolucao,
                e.dt_devolucao,
                e.status_emprestimo,
                c.cod_interno
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            ORDER BY e.dt_emprestimo DESC
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
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)

        # 1. Encontrar uma cópia disponível do livro
        cursor.execute("""
            SELECT id_copia FROM copias 
            WHERE id_livro = %s AND status_copia = 'disponivel' 
            LIMIT 1
        """, (id_livro,))
        copia = cursor.fetchone()
        
        if not copia:
            return False, "Não há cópias disponíveis deste livro."

        id_copia = copia['id_copia']

        # 2. Verificar se o usuário tem multas pendentes
        cursor.execute("""
            SELECT * FROM multas 
            WHERE id_emprestimo IN (
                SELECT id_emprestimo FROM emprestimos 
                WHERE id_usuario = %s
            ) AND status_multa = 'pendente'
        """, (id_usuario,))
        
        if cursor.fetchone():
            return False, "Usuário possui multas pendentes e não pode realizar empréstimos."

        # 3. Realizar o empréstimo
        dt_emprestimo = datetime.now()
        dt_prevista_devolucao = dt_emprestimo + timedelta(days=14)  # Prazo de 14 dias
        
        cursor.execute("""
            INSERT INTO emprestimos 
            (id_usuario, id_copia, dt_emprestimo, dt_prevista_devolucao, status_emprestimo) 
            VALUES (%s, %s, %s, %s, 'ativo')
        """, (id_usuario, id_copia, dt_emprestimo, dt_prevista_devolucao))
        
        # 4. Atualizar o status da cópia para emprestado
        cursor.execute("""
            UPDATE copias SET status_copia = 'emprestado' 
            WHERE id_copia = %s
        """, (id_copia,))
        
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
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT e.*, l.titulo, u.nome_completo, c.cod_interno 
            FROM emprestimos e 
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.id_emprestimo = %s
        """
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
        conn = DBConexao()
        cursor = conn.cursor()
        # Adicionar mais 14 dias à data de devolução prevista
        cursor.execute("""
            UPDATE emprestimos 
            SET dt_prevista_devolucao = dt_prevista_devolucao + INTERVAL 14 DAY 
            WHERE id_emprestimo = %s AND status_emprestimo = 'ativo'
        """, (id_emprestimo,))
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
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Pegar dados do empréstimo
        cursor.execute("SELECT * FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
        emprestimo = cursor.fetchone()
        if not emprestimo:
            return False, "Empréstimo não encontrado."

        id_copia = emprestimo['id_copia']
        dt_prevista_devolucao = emprestimo['dt_prevista_devolucao']

        # 2. Atualizar a data de devolução para a data atual
        dt_devolucao_real = datetime.now()
        cursor.execute("""
            UPDATE emprestimos 
            SET dt_devolucao = %s, status_emprestimo = 'devolvido' 
            WHERE id_emprestimo = %s
        """, (dt_devolucao_real, id_emprestimo))

        # 3. Atualizar status da cópia para disponível
        cursor.execute("""
            UPDATE copias SET status_copia = 'disponivel' 
            WHERE id_copia = %s
        """, (id_copia,))

        # 4. Verificar se há multa por atraso
        if dt_devolucao_real > dt_prevista_devolucao:
            dias_atraso = (dt_devolucao_real - dt_prevista_devolucao).days
            valor_multa = dias_atraso * 1.50  # R$ 1,50 por dia de atraso
            cursor.execute("""
                INSERT INTO multas 
                (id_emprestimo, valor, status_multa, dt_criacao) 
                VALUES (%s, %s, 'pendente', %s)
            """, (id_emprestimo, valor_multa, dt_devolucao_real))

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
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        today = datetime.now()
        sql = """
            SELECT 
                e.id_emprestimo, 
                l.titulo, 
                u.nome_completo, 
                e.dt_emprestimo, 
                e.dt_prevista_devolucao,
                DATEDIFF(%s, e.dt_prevista_devolucao) as dias_atraso
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.dt_prevista_devolucao < %s 
            AND e.status_emprestimo = 'ativo'
            AND e.dt_devolucao IS NULL
        """
        cursor.execute(sql, (today, today))
        emprestimos = cursor.fetchall()
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos atrasados: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarEmprestimosPorUsuario(id_usuario):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT e.id_emprestimo, l.titulo, e.dt_emprestimo, e.dt_prevista_devolucao 
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            WHERE e.id_usuario = %s AND e.status_emprestimo = 'ativo'
        """
        cursor.execute(sql, (id_usuario,))
        emprestimos = cursor.fetchall()
        cursor.close()
        return True, emprestimos
    except Exception as e:
        print(f"[ListarEmprestimosPorUsuario] ERRO: {e}")
        return False, "Erro ao buscar empréstimos do usuário"
    finally:
        if conn and conn.is_connected():
            conn.close()