import mysql.connector
from configDB import DBConexao

class Multa:
    def __init__(self, id_multa=None, id_usuario=None, id_emprestimo=None, 
                 valor_multa=None, data_multa=None, paga=None, nome_completo=None):
        self.id_multa = id_multa
        self.id_usuario = id_usuario
        self.id_emprestimo = id_emprestimo
        self.valor_multa = valor_multa
        self.data_multa = data_multa
        self.paga = paga
        self.nome_completo = nome_completo

    def __str__(self):
        return f"Multa {self.id_multa} - {self.nome_completo} - R$ {self.valor_multa} - {'Paga' if self.paga else 'Pendente'}"

    def to_dict(self):
        """Converte o objeto Multa para dicionário"""
        return {
            'id_multa': self.id_multa,
            'id_usuario': self.id_usuario,
            'id_emprestimo': self.id_emprestimo,
            'valor_multa': self.valor_multa,
            'data_multa': self.data_multa,
            'paga': self.paga,
            'nome_completo': self.nome_completo
        }

class MultaController:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def _conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = DBConexao()
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

    def listar_multas(self, apenas_pendentes=False):
        """
        Lista todas as multas
        
        Args:
            apenas_pendentes (bool): Se True, lista apenas multas não pagas
        """
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            sql = """
                SELECT 
                    m.id_multa, 
                    u.nome_completo, 
                    m.valor_multa, 
                    m.data_multa,
                    m.paga,
                    m.id_usuario,
                    m.id_emprestimo
                FROM multas m
                JOIN usuarios u ON m.id_usuario = u.id_usuario
            """
            
            if apenas_pendentes:
                sql += " WHERE m.paga = FALSE"
            
            self.cursor.execute(sql)
            resultados = self.cursor.fetchall()
            
            # Converter para objetos Multa
            multas = []
            for resultado in resultados:
                multa = Multa(
                    id_multa=resultado['id_multa'],
                    id_usuario=resultado['id_usuario'],
                    nome_completo=resultado['nome_completo'],
                    valor_multa=resultado['valor_multa'],
                    data_multa=resultado['data_multa'],
                    paga=resultado['paga'],
                    id_emprestimo=resultado.get('id_emprestimo')
                )
                multas.append(multa)
            
            return True, multas
            
        except mysql.connector.Error as err:
            return False, f"Erro ao listar multas: {err}"
        finally:
            self._desconectar()

    def pegar_multa_por_id(self, id_multa):
        """Busca uma multa pelo ID"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            sql = """SELECT m.*, u.nome_completo FROM multas m
                     JOIN usuarios u ON m.id_usuario = u.id_usuario
                     WHERE m.id_multa = %s"""
            self.cursor.execute(sql, (id_multa,))
            resultado = self.cursor.fetchone()
            
            if not resultado:
                return False, "Multa não encontrada."
            
            # Converter para objeto Multa
            multa = Multa(
                id_multa=resultado['id_multa'],
                id_usuario=resultado['id_usuario'],
                id_emprestimo=resultado.get('id_emprestimo'),
                valor_multa=resultado['valor_multa'],
                data_multa=resultado['data_multa'],
                paga=resultado['paga'],
                nome_completo=resultado['nome_completo']
            )
            
            return True, multa
            
        except mysql.connector.Error as err:
            return False, f"Erro ao buscar multa: {err}"
        finally:
            self._desconectar()

    def remover_multa(self, id_multa):
        """Marca uma multa como paga (remoção lógica)"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            # Verificar se a multa existe
            self.cursor.execute("SELECT id_multa FROM multas WHERE id_multa = %s", (id_multa,))
            if not self.cursor.fetchone():
                return False, "Multa não encontrada."
            
            # Marcar a multa como paga
            self.cursor.execute("UPDATE multas SET paga = TRUE WHERE id_multa = %s", (id_multa,))
            self.conn.commit()
            
            return True, "Multa removida (paga) com sucesso!"
            
        except mysql.connector.Error as err:
            if self.conn:
                self.conn.rollback()
            return False, f"Erro ao remover multa: {err}"
        finally:
            self._desconectar()

    def criar_multa(self, id_emprestimo, id_usuario, valor_multa, data_multa=None):
        """Cria uma nova multa"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            if data_multa is None:
                from datetime import date
                data_multa = date.today()
            
            self.cursor.execute(
                "INSERT INTO multas (id_emprestimo, id_usuario, valor_multa, data_multa, paga) VALUES (%s, %s, %s, %s, %s)",
                (id_emprestimo, id_usuario, valor_multa, data_multa, False)
            )
            self.conn.commit()
            
            id_nova_multa = self.cursor.lastrowid
            return True, id_nova_multa
            
        except mysql.connector.Error as err:
            if self.conn:
                self.conn.rollback()
            return False, f"Erro ao criar multa: {err}"
        finally:
            self._desconectar()

    def calcular_total_multas_pendentes(self, id_usuario=None):
        """Calcula o total de multas pendentes"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            if id_usuario:
                sql = "SELECT SUM(valor_multa) as total FROM multas WHERE paga = FALSE AND id_usuario = %s"
                self.cursor.execute(sql, (id_usuario,))
            else:
                sql = "SELECT SUM(valor_multa) as total FROM multas WHERE paga = FALSE"
                self.cursor.execute(sql)
            
            resultado = self.cursor.fetchone()
            total = resultado['total'] or 0.0
            
            return True, total
            
        except mysql.connector.Error as err:
            return False, f"Erro ao calcular total de multas: {err}"
        finally:
            self._desconectar()

    def verificar_usuario_com_multas_pendentes(self, id_usuario):
        """Verifica se um usuário possui multas pendentes"""
        try:
            if not self._conectar():
                return False, "Erro ao conectar ao banco de dados"
            
            self.cursor.execute(
                "SELECT COUNT(*) as count FROM multas WHERE id_usuario = %s AND paga = FALSE",
                (id_usuario,)
            )
            resultado = self.cursor.fetchone()
            tem_multas = resultado['count'] > 0
            
            return True, tem_multas
            
        except mysql.connector.Error as err:
            return False, f"Erro ao verificar multas do usuário: {err}"
        finally:
            self._desconectar()

# Funções de interface para manter compatibilidade com o código existente
def ListarMultas():
    controller = MultaController()
    return controller.listar_multas()

def PegaMultaPorId(id_multa):
    controller = MultaController()
    return controller.pegar_multa_por_id(id_multa)

def RemoverMulta(id_multa):
    controller = MultaController()
    return controller.remover_multa(id_multa)