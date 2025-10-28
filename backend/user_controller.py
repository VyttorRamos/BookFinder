# user_controller.py
from configDB import DBConexao
from user import User
from auth.auth_utils import SenhaHash, VerificaSenha

class UserController:
    
    @staticmethod
    def get_user_by_email(email: str):
        conn = None
        try:
            conn = DBConexao()
            if not conn:
                return None

            cursor = conn.cursor(dictionary=True)
            sql = (
                "SELECT id_usuario, nome_completo, email, senha, telefone, "
                "tipo_usuario, status_usuario FROM usuarios WHERE email = %s LIMIT 1"
            )
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return User(**result)
            return None
            
        except Exception as e:
            print(f"[get_user_by_email] ERRO: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_user_by_id(user_id: int):
        conn = None
        try:
            conn = DBConexao()
            if not conn:
                return None

            cursor = conn.cursor(dictionary=True)
            sql = (
                "SELECT id_usuario, nome_completo, email, senha, telefone, "
                "tipo_usuario, status_usuario FROM usuarios WHERE id_usuario = %s LIMIT 1"
            )
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return User(**result)
            return None
            
        except Exception as e:
            print(f"[get_user_by_id] ERRO: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def get_all_users():
        conn = None
        try:
            conn = DBConexao()
            if not conn:
                return None

            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id_usuario, nome_completo, email, telefone, tipo_usuario, status_usuario FROM usuarios"
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            
            users = []
            for result in results:
                users.append(User(**result))
            return users
            
        except Exception as e:
            print(f"[get_all_users] ERRO: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def create_user(user: User):
        conn = None
        try:
            # Verifica se email já existe
            existing_user = UserController.get_user_by_email(user.email)
            if existing_user:
                return False, "Email já cadastrado"

            user.senha = SenhaHash(user.senha)

            conn = DBConexao()
            if not conn:
                return False, "Falha na conexão com o DB"

            cursor = conn.cursor()
            sql = (
                "INSERT INTO usuarios (nome_completo, email, senha, telefone, tipo_usuario) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(sql, (user.nome_completo, user.email, user.senha, 
                               user.telefone, user.tipo_usuario))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            return True, user_id
            
        except Exception as e:
            print(f"[create_user] ERRO: {e}")
            return False, "Erro ao criar usuário"
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def update_user(user_id: int, user_data: dict):
        conn = None
        try:
            conn = DBConexao()
            if not conn:
                return False, "Falha na conexão com o DB"

            cursor = conn.cursor()
            
            # Constrói a query dinamicamente baseado nos campos fornecidos
            fields = []
            values = []
            
            if 'nome_completo' in user_data:
                fields.append("nome_completo = %s")
                values.append(user_data['nome_completo'])
            
            if 'email' in user_data:
                fields.append("email = %s")
                values.append(user_data['email'])
            
            if 'telefone' in user_data:
                fields.append("telefone = %s")
                values.append(user_data['telefone'])
            
            if 'tipo_usuario' in user_data:
                fields.append("tipo_usuario = %s")
                values.append(user_data['tipo_usuario'])
            
            if 'senha' in user_data and user_data['senha']:
                fields.append("senha = %s")
                values.append(SenhaHash(user_data['senha']))
            
            fields.append("dt_alteracao = NOW()")
            
            if not fields:
                return False, "Nenhum campo para atualizar"
            
            values.append(user_id)
            sql = f"UPDATE usuarios SET {', '.join(fields)} WHERE id_usuario = %s"
            
            cursor.execute(sql, values)
            conn.commit()
            cursor.close()
            return True, "Usuário atualizado com sucesso"
            
        except Exception as e:
            print(f"[update_user] ERRO: {e}")
            return False, f"Erro ao atualizar usuário: {str(e)}"
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def delete_user(user_id: int):
        conn = None
        try:
            conn = DBConexao()
            if not conn:
                return False, "Falha na conexão com o DB"

            cursor = conn.cursor()
            sql = "DELETE FROM usuarios WHERE id_usuario = %s"
            cursor.execute(sql, (user_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            if affected_rows > 0:
                return True, "Usuário excluído com sucesso"
            else:
                return False, "Usuário não encontrado"
            
        except Exception as e:
            print(f"[delete_user] ERRO: {e}")
            return False, f"Erro ao excluir usuário: {str(e)}"
        finally:
            if conn and conn.is_connected():
                conn.close()

    @staticmethod
    def verify_login(email: str, password: str):
        user = UserController.get_user_by_email(email)
        if not user:
            return False, "Credenciais inválidas"

        valid, new_hash = VerificaSenha(user.senha, password)
        if not valid:
            return False, "Credenciais inválidas"
        
        is_admin = user.tipo_usuario == "admin"
        
        # Remove a senha do objeto user para segurança
        user_dict = user.to_dict()
        
        return True, {
            "usuario": user_dict, 
            "novaHash": new_hash, 
            "is_admin": is_admin
        }