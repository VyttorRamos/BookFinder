import mysql.connector
from configDB import DBConexao
from datetime import datetime, timedelta
from configModel import BuscarConfiguracoes

def ObterConfiguracoesEmprestimo():
    """Busca configurações do sistema para empréstimos"""
    ok, configuracoes = BuscarConfiguracoes()
    if not ok:
        # Valores padrão caso as configurações não existam
        return {
            'limite_emprestimos': 3,
            'prazo_aluno': 15,
            'prazo_professor': 30,
            'limite_renovacoes': 1,
            'dias_renovacao': 15,
            'multa_por_dia': 2.00
        }
    
    config_dict = {}
    default_values = {
        'limite_emprestimos': 3,
        'prazo_aluno': 15,
        'prazo_professor': 30,
        'limite_renovacoes': 1,
        'dias_renovacao': 15,
        'multa_por_dia': 2.00
    }
    
    for chave, default in default_values.items():
        if chave in configuracoes:
            if chave in ['limite_emprestimos', 'prazo_aluno', 'prazo_professor', 'limite_renovacoes', 'dias_renovacao']:
                config_dict[chave] = int(configuracoes[chave]['valor'])
            elif chave == 'multa_por_dia':
                config_dict[chave] = float(configuracoes[chave]['valor'])
        else:
            config_dict[chave] = default
    
    return config_dict

def ListarEmprestimos():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                e.id_emprestimo,
                l.titulo,
                u.nome_completo,
                u.id_usuario,
                e.dt_emprestimo,
                e.dt_prevista_devolucao,
                e.dt_devolucao,
                e.status_emprestimo as status,
                l.id_livro,
                c.cod_interno,
                c.id_copia,
                e.renovado
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.status_emprestimo IN ('ativo', 'atrasado')
            ORDER BY e.dt_emprestimo DESC
        """
        cursor.execute(sql)
        emprestimos = cursor.fetchall()
        
        # Atualizar status para atrasado se necessário
        hoje = datetime.now().date()
        for emprestimo in emprestimos:
            if (emprestimo['status'] == 'ativo' and 
                emprestimo['dt_prevista_devolucao'] and 
                emprestimo['dt_prevista_devolucao'].date() < hoje):
                emprestimo['status'] = 'atrasado'
                
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def BuscarLivrosDisponiveis(termo_busca=None):
    """Busca livros disponíveis com opção de filtro por título ou ISBN"""
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        
        if termo_busca:
            sql = """
                SELECT l.*, e.nome as editora_nome, c.nome as categoria_nome 
                FROM livros l 
                LEFT JOIN editoras e ON l.id_editora = e.id_editora 
                LEFT JOIN categorias c ON l.id_categoria = c.id_categoria 
                WHERE l.status_livro = 'ativo'
                AND (l.titulo LIKE %s OR l.isbn LIKE %s)
                AND l.quantidade_disponivel > 0
                ORDER BY l.titulo
            """
            cursor.execute(sql, (f'%{termo_busca}%', f'%{termo_busca}%'))
        else:
            sql = """
                SELECT l.*, e.nome as editora_nome, c.nome as categoria_nome 
                FROM livros l 
                LEFT JOIN editoras e ON l.id_editora = e.id_editora 
                LEFT JOIN categorias c ON l.id_categoria = c.id_categoria 
                WHERE l.status_livro = 'ativo'
                AND l.quantidade_disponivel > 0
                ORDER BY l.titulo
            """
            cursor.execute(sql)
        
        livros = cursor.fetchall()
        return True, livros
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar livros: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def RealizarEmprestimo(id_livro, id_usuario):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)

        # Obter configurações do sistema
        config = ObterConfiguracoesEmprestimo()

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
            WHERE id_usuario = %s AND status_multa = 'pendente'
        """, (id_usuario,))
        
        if cursor.fetchone():
            return False, "Usuário possui multas pendentes e não pode realizar empréstimos."

        # 3. Verificar se o usuário já tem este livro emprestado
        cursor.execute("""
            SELECT * FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            WHERE c.id_livro = %s AND e.id_usuario = %s AND e.status_emprestimo = 'ativo'
        """, (id_livro, id_usuario))
        
        if cursor.fetchone():
            return False, "Usuário já possui este livro emprestado."

        # 4. Verificar limite de empréstimos do usuário
        cursor.execute("""
            SELECT COUNT(*) as total_emprestimos 
            FROM emprestimos 
            WHERE id_usuario = %s AND status_emprestimo = 'ativo'
        """, (id_usuario,))
        
        total_emprestimos = cursor.fetchone()['total_emprestimos']
        
        if total_emprestimos >= config['limite_emprestimos']:
            return False, f"Usuário atingiu o limite máximo de {config['limite_emprestimos']} empréstimos simultâneos."

        # 5. Realizar o empréstimo
        dt_emprestimo = datetime.now()
        
        # Definir prazo de devolução baseado no tipo de usuário
        cursor.execute("SELECT tipo_usuario FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        
        if usuario['tipo_usuario'] == 'professor':
            dias_emprestimo = config['prazo_professor']
        else:
            dias_emprestimo = config['prazo_aluno']
            
        dt_prevista_devolucao = dt_emprestimo + timedelta(days=dias_emprestimo)
        
        cursor.execute("""
            INSERT INTO emprestimos 
            (id_usuario, id_copia, dt_emprestimo, dt_prevista_devolucao, status_emprestimo, renovado) 
            VALUES (%s, %s, %s, %s, 'ativo', 0)
        """, (id_usuario, id_copia, dt_emprestimo, dt_prevista_devolucao))
        
        # 6. Atualizar o status da cópia para emprestado
        cursor.execute("""
            UPDATE copias SET status_copia = 'emprestado' 
            WHERE id_copia = %s
        """, (id_copia,))
        
        # 7. Atualizar quantidade disponível do livro
        cursor.execute("""
            UPDATE livros 
            SET quantidade_disponivel = quantidade_disponivel - 1 
            WHERE id_livro = %s AND quantidade_disponivel > 0
        """, (id_livro,))
        
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
            SELECT e.*, l.titulo, u.nome_completo, c.cod_interno, l.id_livro, u.tipo_usuario,
                   e.dt_emprestimo as data_emprestimo,
                   e.dt_prevista_devolucao as dt_devolucao_prevista
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
        cursor = conn.cursor(dictionary=True)
        
        # Obter configurações do sistema
        config = ObterConfiguracoesEmprestimo()
        
        # Buscar dados do empréstimo
        cursor.execute("""
            SELECT e.*, u.tipo_usuario 
            FROM emprestimos e
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.id_emprestimo = %s
        """, (id_emprestimo,))
        emprestimo = cursor.fetchone()
        
        if not emprestimo:
            return False, "Empréstimo não encontrado."
            
        if emprestimo['status_emprestimo'] != 'ativo':
            return False, "Apenas empréstimos ativos podem ser renovados."
            
        # Verificar se já foi renovado antes
        if emprestimo['renovado'] >= config['limite_renovacoes']:
            return False, f"Este empréstimo já atingiu o limite máximo de {config['limite_renovacoes']} renovações."
        
        # Calcular nova data de devolução
        nova_data_prevista = emprestimo['dt_prevista_devolucao'] + timedelta(days=config['dias_renovacao'])
        
        cursor.execute("""
            UPDATE emprestimos 
            SET dt_prevista_devolucao = %s, renovado = renovado + 1 
            WHERE id_emprestimo = %s
        """, (nova_data_prevista, id_emprestimo))
        
        conn.commit()
        return True, f"Empréstimo renovado com sucesso! Nova data de devolução: {nova_data_prevista.strftime('%d/%m/%Y')}"
        
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao renovar empréstimo: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def ListarAtrasados():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        hoje = datetime.now().date()
        
        sql = """
            SELECT 
                e.id_emprestimo,
                l.titulo,
                u.nome_completo,
                u.id_usuario,
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
            ORDER BY e.dt_prevista_devolucao ASC
        """
        cursor.execute(sql, (hoje, hoje))
        emprestimos = cursor.fetchall()
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos atrasados: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarEmprestimosPorUsuario(id_usuario: int):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT 
                e.id_emprestimo,
                e.dt_emprestimo,
                e.dt_prevista_devolucao,
                e.dt_devolucao,
                e.status_emprestimo,
                e.renovado,
                l.titulo,
                l.id_livro,
                c.cod_interno
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            WHERE e.id_usuario = %s 
            AND e.status_emprestimo != 'cancelado'
            ORDER BY e.dt_emprestimo DESC
        """
        cursor.execute(sql, (id_usuario,))
        emprestimos = cursor.fetchall()
        return True, emprestimos
    except Error as err:
        print(f"[ListarEmprestimosPorUsuario] ERRO: {err}")
        return False, f"Erro ao listar empréstimos: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DevolverLivro(id_emprestimo: int):
    conn = None
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        
        # Primeiro, pega as informações do empréstimo
        cursor.execute("""
            SELECT e.id_copia, e.id_usuario, e.dt_prevista_devolucao, c.id_livro 
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            WHERE e.id_emprestimo = %s
        """, (id_emprestimo,))
        emprestimo = cursor.fetchone()
        
        if not emprestimo:
            return False, "Empréstimo não encontrado"
        
        id_copia = emprestimo['id_copia']
        id_usuario = emprestimo['id_usuario']
        id_livro = emprestimo['id_livro']
        
        # Calcular dias de atraso se houver
        dias_atraso = 0
        cursor.execute("SELECT NOW() as data_atual")
        data_atual = cursor.fetchone()['data_atual']
        
        if emprestimo['dt_prevista_devolucao'] and data_atual > emprestimo['dt_prevista_devolucao']:
            from datetime import datetime
            dt_prevista = emprestimo['dt_prevista_devolucao']
            if isinstance(dt_prevista, str):
                dt_prevista = datetime.strptime(dt_prevista, '%Y-%m-%d %H:%M:%S')
            
            dias_atraso = (data_atual - dt_prevista).days
        
        # Atualiza o empréstimo para devolvido
        sql_emprestimo = """
            UPDATE emprestimos 
            SET status_emprestimo = 'devolvido', 
                dt_devolucao = NOW() 
            WHERE id_emprestimo = %s
        """
        cursor.execute(sql_emprestimo, (id_emprestimo,))
        
        # Atualiza a cópia para disponível
        sql_copia = """
            UPDATE copias 
            SET status_copia = 'disponivel' 
            WHERE id_copia = %s
        """
        cursor.execute(sql_copia, (id_copia,))
        
        # Atualiza a quantidade disponível do livro
        cursor.execute("""
            UPDATE livros 
            SET quantidade_disponivel = quantidade_disponivel + 1 
            WHERE id_livro = %s
        """, (id_livro,))
        
        # Se houver atraso, criar multa
        if dias_atraso > 0:
            # Buscar valor da multa por dia
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'multa_por_dia'")
            config = cursor.fetchone()
            valor_multa_por_dia = float(config['valor']) if config else 2.00
            
            valor_multa = dias_atraso * valor_multa_por_dia
            
            sql_multa = """
                INSERT INTO multas (id_emprestimo, id_usuario, valor, status_multa, dias_atraso, dt_criacao)
                VALUES (%s, %s, %s, 'pendente', %s, NOW())
            """
            cursor.execute(sql_multa, (id_emprestimo, id_usuario, valor_multa, dias_atraso))
        
        conn.commit()
        return True, "Livro devolvido com sucesso"
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[DevolverLivro] ERRO: {e}")
        return False, f"Erro ao devolver livro: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def VerificarAtrasosUsuario(id_usuario):
    """Verifica se usuário tem empréstimos em atraso"""
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        hoje = datetime.now().date()
        
        sql = """
            SELECT COUNT(*) as total_atrasos
            FROM emprestimos 
            WHERE id_usuario = %s 
            AND status_emprestimo = 'ativo'
            AND dt_prevista_devolucao < %s
        """
        cursor.execute(sql, (id_usuario, hoje))
        resultado = cursor.fetchone()
        return True, resultado['total_atrasos'] > 0
    except Exception as e:
        return False, f"Erro ao verificar atrasos: {str(e)}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def ListarEmprestimosComBusca(termo_busca):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT 
                e.id_emprestimo,
                l.titulo,
                u.nome_completo,
                u.id_usuario,
                e.dt_emprestimo,
                e.dt_prevista_devolucao,
                e.dt_devolucao,
                e.status_emprestimo as status,
                l.id_livro,
                c.cod_interno,
                c.id_copia,
                e.renovado
            FROM emprestimos e
            JOIN copias c ON e.id_copia = c.id_copia
            JOIN livros l ON c.id_livro = l.id_livro
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.status_emprestimo IN ('ativo', 'atrasado')
            AND (u.nome_completo LIKE %s OR l.titulo LIKE %s OR u.email LIKE %s)
            ORDER BY e.dt_emprestimo DESC
        """
        
        termo_like = f'%{termo_busca}%'
        cursor.execute(sql, (termo_like, termo_like, termo_like))
        emprestimos = cursor.fetchall()
        
        # Atualizar status para atrasado se necessário
        hoje = datetime.now().date()
        for emprestimo in emprestimos:
            if (emprestimo['status'] == 'ativo' and 
                emprestimo['dt_prevista_devolucao'] and 
                emprestimo['dt_prevista_devolucao'].date() < hoje):
                emprestimo['status'] = 'atrasado'
                
        return True, emprestimos
    except mysql.connector.Error as err:
        return False, f"Erro ao listar empréstimos: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()