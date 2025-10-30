import mysql.connector
from db_connection import get_db_connection
from datetime import date, timedelta

class Emprestimo:
    def __init__(self, id_emprestimo=None, id_livro=None, id_usuario=None, 
                 data_emprestimo=None, data_devolucao=None, titulo=None, nome_completo=None):
        self.id_emprestimo = id_emprestimo
        self.id_livro = id_livro
        self.id_usuario = id_usuario
        self.data_emprestimo = data_emprestimo
        self.data_devolucao = data_devolucao
        self.titulo = titulo
        self.nome_completo = nome_completo

class EmprestimoController:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def _conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = get_db_connection()
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco: {err}")
            return False

    def _desconectar(self):
        """Fecha conexão com o banco de dados"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def listar_emprestimos(self):
        """Lista todos os empréstimos ativos"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
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
            self.cursor.execute(sql)
            resultados = self.cursor.fetchall()
            
            # Converter para objetos Emprestimo
            emprestimos = []
            for resultado in resultados:
                emprestimo = Emprestimo(
                    id_emprestimo=resultado['id_emprestimo'],
                    titulo=resultado['titulo'],
                    nome_completo=resultado['nome_completo'],
                    data_emprestimo=resultado['data_emprestimo'],
                    data_devolucao=resultado['data_devolucao']
                )
                emprestimos.append(emprestimo)
            
            return True, emprestimos
            
        except mysql.connector.Error as err:
            return False, f"Erro ao listar empréstimos: {err}"
        finally:
            self._desconectar()

    def realizar_emprestimo(self, id_livro, id_usuario):
        """Realiza um novo empréstimo"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"

            # 1. Verificar se o livro está disponível
            self.cursor.execute("SELECT disponivel FROM livros WHERE id_livro = %s", (id_livro,))
            livro = self.cursor.fetchone()
            if not livro or not livro['disponivel']:
                return False, "Livro não está disponível para empréstimo."

            # 2. Verificar se o usuário tem multas pendentes
            self.cursor.execute("SELECT * FROM multas WHERE id_usuario = %s AND paga = FALSE", (id_usuario,))
            if self.cursor.fetchone():
                return False, "Usuário possui multas pendentes e não pode realizar empréstimos."

            # 3. Realizar o empréstimo
            data_emprestimo = date.today()
            data_devolucao_prevista = data_emprestimo + timedelta(days=14)
            
            self.cursor.execute(
                "INSERT INTO emprestimos (id_livro, id_usuario, data_emprestimo, data_devolucao) VALUES (%s, %s, %s, %s)", 
                (id_livro, id_usuario, data_emprestimo, data_devolucao_prevista)
            )
            
            # 4. Atualizar o status do livro para indisponível
            self.cursor.execute("UPDATE livros SET disponivel = FALSE WHERE id_livro = %s", (id_livro,))
            
            self.conn.commit()
            return True, "Empréstimo realizado com sucesso!"
            
        except mysql.connector.Error as err:
            if self.conn:
                self.conn.rollback()
            return False, f"Erro ao realizar empréstimo: {err}"
        finally:
            self._desconectar()

    def pegar_emprestimo_por_id(self, id_emprestimo):
        """Busca um empréstimo pelo ID"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            sql = """SELECT e.*, l.titulo, u.nome_completo FROM emprestimos e 
                     JOIN livros l ON e.id_livro = l.id_livro
                     JOIN usuarios u ON e.id_usuario = u.id_usuario
                     WHERE e.id_emprestimo = %s"""
            self.cursor.execute(sql, (id_emprestimo,))
            resultado = self.cursor.fetchone()
            
            if not resultado:
                return False, "Empréstimo não encontrado."
            
            # Converter para objeto Emprestimo
            emprestimo = Emprestimo(
                id_emprestimo=resultado['id_emprestimo'],
                id_livro=resultado['id_livro'],
                id_usuario=resultado['id_usuario'],
                data_emprestimo=resultado['data_emprestimo'],
                data_devolucao=resultado['data_devolucao'],
                titulo=resultado['titulo'],
                nome_completo=resultado['nome_completo']
            )
            
            return True, emprestimo
            
        except mysql.connector.Error as err:
            return False, f"Erro ao buscar empréstimo: {err}"
        finally:
            self._desconectar()

    def renovar_emprestimo(self, id_emprestimo):
        """Renova um empréstimo por mais 14 dias"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            # Adicionar mais 14 dias à data de devolução
            self.cursor.execute(
                "UPDATE emprestimos SET data_devolucao = data_devolucao + INTERVAL 14 DAY WHERE id_emprestimo = %s", 
                (id_emprestimo,)
            )
            self.conn.commit()
            return True, "Empréstimo renovado com sucesso!"
            
        except mysql.connector.Error as err:
            if self.conn:
                self.conn.rollback()
            return False, f"Erro ao renovar empréstimo: {err}"
        finally:
            self._desconectar()

    def devolver_livro(self, id_emprestimo):
        """Processa a devolução de um livro"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            # 1. Pegar dados do empréstimo
            self.cursor.execute("SELECT * FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
            resultado = self.cursor.fetchone()
            if not resultado:
                return False, "Empréstimo não encontrado."

            id_livro = resultado['id_livro']
            id_usuario = resultado['id_usuario']
            data_devolucao_prevista = resultado['data_devolucao']

            # 2. Atualizar a data de devolução para a data atual
            data_devolucao_real = date.today()
            self.cursor.execute(
                "UPDATE emprestimos SET data_devolucao = %s WHERE id_emprestimo = %s", 
                (data_devolucao_real, id_emprestimo)
            )

            # 3. Atualizar status do livro para disponível
            self.cursor.execute("UPDATE livros SET disponivel = TRUE WHERE id_livro = %s", (id_livro,))

            # 4. Verificar se há multa
            if data_devolucao_real > data_devolucao_prevista:
                dias_atraso = (data_devolucao_real - data_devolucao_prevista).days
                valor_multa = dias_atraso * 1.50  # R$ 1,50 por dia de atraso
                self.cursor.execute(
                    "INSERT INTO multas (id_emprestimo, id_usuario, valor_multa, data_multa) VALUES (%s, %s, %s, %s)",
                    (id_emprestimo, id_usuario, valor_multa, data_devolucao_real)
                )

            self.conn.commit()
            return True, "Livro devolvido com sucesso!"
            
        except mysql.connector.Error as err:
            if self.conn:
                self.conn.rollback()
            return False, f"Erro ao devolver livro: {err}"
        finally:
            self._desconectar()

    def listar_atrasados(self):
        """Lista todos os empréstimos atrasados"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
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
            self.cursor.execute(sql, (today,))
            resultados = self.cursor.fetchall()
            
            # Converter para objetos Emprestimo
            emprestimos = []
            for resultado in resultados:
                emprestimo = Emprestimo(
                    id_emprestimo=resultado['id_emprestimo'],
                    titulo=resultado['titulo'],
                    nome_completo=resultado['nome_completo'],
                    data_emprestimo=resultado['data_emprestimo'],
                    data_devolucao=resultado['data_devolucao']
                )
                emprestimos.append(emprestimo)
            
            return True, emprestimos
            
        except mysql.connector.Error as err:
            return False, f"Erro ao listar empréstimos atrasados: {err}"
        finally:
            self._desconectar()

# Funções de interface para manter compatibilidade com o código existente
def ListarEmprestimos():
    controller = EmprestimoController()
    return controller.listar_emprestimos()

def RealizarEmprestimo(id_livro, id_usuario):
    controller = EmprestimoController()
    return controller.realizar_emprestimo(id_livro, id_usuario)

def PegaEmprestimoPorId(id_emprestimo):
    controller = EmprestimoController()
    return controller.pegar_emprestimo_por_id(id_emprestimo)

def RenovarEmprestimo(id_emprestimo):
    controller = EmprestimoController()
    return controller.renovar_emprestimo(id_emprestimo)

def DevolverLivro(id_emprestimo):
    controller = EmprestimoController()
    return controller.devolver_livro(id_emprestimo)

def ListarAtrasados():
    controller = EmprestimoController()
    return controller.listar_atrasados()