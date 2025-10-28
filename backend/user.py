# user.py
from configDB import DBConexao
from auth.auth_utils import SenhaHash, VerificaSenha

class User:
    def __init__(self, id_usuario=None, nome_completo=None, email=None, senha=None, 
                 telefone=None, tipo_usuario="aluno", status_usuario="ativo"):
        self.id_usuario = id_usuario
        self.nome_completo = nome_completo
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.tipo_usuario = tipo_usuario
        self.status_usuario = status_usuario
    
    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nome_completo": self.nome_completo,
            "email": self.email,
            "telefone": self.telefone,
            "tipo_usuario": self.tipo_usuario,
            "status_usuario": self.status_usuario
        }