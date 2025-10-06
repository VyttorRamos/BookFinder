from configDB import DBConexao
from mysql.connector import Error
from auth.auth_utils import SenhaHash, VerificaSenha

#Retorna o usuário ou None se não existir 
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
        #print(f"[PegaUserPorEmail] ERRO: {e}")
        return None
    finally:
        if conn and getattr(conn, "is_connected", lambda: False)():
            conn.close()

#Tenta criar um usuário e retorna true, id_usuario em sucesso ou false, mensagem de erro em falha
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
        #não vaza mensagem sensivel
        print(f"[CadastroUser] ERRO: {e}")
        return False, "Erro ao criar usuário"
    finally:
        if conn and getattr(conn, "is_connected", lambda: False)():
            conn.close()


#retorna true, user se correto e retorna false, mensagem se incorreto ou erro 
def VerificaLoginUsuario(email: str, SenhaSimples: str):
    usuario = PegaUserPorEmail(email)
    if not usuario:
        return False, "Credenciais inválidas"

    SenhaArmazenada = usuario.get("senha")
    Valido, NovaHash = VerificaSenha(SenhaArmazenada, SenhaSimples)
    if not Valido:
        return False, "Credenciais inválidas"

    # remove o hash do objeto para segurança
    usuario.pop("senha", None)
    return True, {"usuario": usuario, "novaHash": NovaHash}