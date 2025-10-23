from configDB import DBConexao
from mysql.connector import Error
from auth.auth_utils import SenhaHash, VerificaSenha

# def PegaTipoUsuario(email: str):
#     conn = None
#     try:
#         conn = DBConexao()
#         if not conn:
#             return None

#         cursor = conn.cursor()
#         sql = "SELECT tipo_usuario FROM usuarios WHERE email = %s LIMIT 1"
#         cursor.execute(sql, (email,))
#         result = cursor.fetchone()
#         cursor.close()

#         if result:
#             return result[0]  # tipo_usuario
#         else:
#             return None

#     except Exception as e:
#         print(f"[PegaTipoUsuario] ERRO: {e}")
#         return None
#     finally:
#         if conn and conn.is_connected():
#             conn.close()


# def VerificaAdmin(email: str):
#     tipo = PegaTipoUsuario(email)
#     if tipo == 'admin':
#         return True
#     else:
#         return False

def PegaUserPorEmail(email: str):
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
        user = cursor.fetchone()
        cursor.close()
        return user
    except Exception as e:
        print(f"[PegaUserPorEmail] ERRO: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def CadastroUser(nome_completo: str, email: str, plain_password: str,
                 telefone: str = None, tipo_usuario: str = "aluno"):
    conn = None
    try:
        existe = PegaUserPorEmail(email)
        if existe:
            return False, "Email já cadastrado"

        password_hash = SenhaHash(plain_password)

        conn = DBConexao()
        if not conn:
            return False, "Falha na conexão com o DB"

        cursor = conn.cursor()
        sql = (
            "INSERT INTO usuarios (nome_completo, email, senha, telefone, tipo_usuario) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        cursor.execute(sql, (nome_completo, email, password_hash, telefone, tipo_usuario))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return True, user_id
    except Exception as e:
        print(f"[CadastroUser] ERRO: {e}")
        return False, "Erro ao criar usuário"
    finally:
        if conn and conn.is_connected():
            conn.close()

def VerificaLoginUsuario(email: str, SenhaSimples: str):
    usuario = PegaUserPorEmail(email)
    if not usuario:
        return False, "Credenciais inválidas"

    SenhaArmazenada = usuario.get("senha")
    
    # Verifica senha com Argon2
    Valido, NovaHash = VerificaSenha(SenhaArmazenada, SenhaSimples)
    if not Valido:
        return False, "Credenciais inválidas"
    
    #Verifica se o usuário é admin
    tipo = usuario.get("tipo_usuario") 
    is_admin = True if tipo == "admin" else False

    # Remove o hash do objeto para segurança antes de retornar
    usuario.pop("senha", None)

    # Retornamos também se é admin para que a camada superior rota/login
    return True, {"usuario": usuario, "novaHash": NovaHash, "is_admin": is_admin}

    # Remove o hash do objeto para segurança
    usuario.pop("senha", None)
    return True, {"usuario": usuario, "novaHash": NovaHash}

    
    

def AtualizaHashSenha(id_usuario: int, new_hash: str):
    conn = None
    try:
        conn = DBConexao()
        if not conn:
            return False
        cursor = conn.cursor()
        sql = "UPDATE usuarios SET senha = %s, dt_alteracao = NOW() WHERE id_usuario = %s"
        cursor.execute(sql, (new_hash, id_usuario))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print("[userModel] Erro AtualizarHashSenha:", e)
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()