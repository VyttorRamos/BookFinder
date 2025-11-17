import mysql.connector
from configDB import DBConexao

def ListarCopias():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM copias")
        copias = cursor.fetchall()
        return True, copias
    except mysql.connector.Error as err:
        return False, f"Erro ao listar cópias: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def CadastrarCopia(id_livro, cod_interno=None, status_copia='disponivel'):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO copias (id_livro, cod_interno, status_copia) VALUES (%s, %s, %s)",
                       (id_livro, cod_interno, status_copia))
        conn.commit()
        return True, "Cópia cadastrada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar cópia: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def PegaCopiaPorId(id_copia):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM copias WHERE id_copia = %s", (id_copia,))
        copia = cursor.fetchone()
        if not copia:
            return False, "Cópia não encontrada."
        return True, copia
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar cópia: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarCopia(id_copia, id_livro=None, cod_interno=None, status_copia=None):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        # build simple update
        parts = []
        vals = []
        if id_livro is not None:
            parts.append('id_livro = %s')
            vals.append(id_livro)
        if cod_interno is not None:
            parts.append('cod_interno = %s')
            vals.append(cod_interno)
        if status_copia is not None:
            parts.append('status_copia = %s')
            vals.append(status_copia)
        if not parts:
            return False, 'Nada para atualizar.'
        vals.append(id_copia)
        sql = f"UPDATE copias SET {', '.join(parts)} WHERE id_copia = %s"
        cursor.execute(sql, tuple(vals))
        conn.commit()
        return True, 'Cópia atualizada com sucesso!'
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar cópia: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def DeletarCopia(id_copia):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM copias WHERE id_copia = %s", (id_copia,))
        conn.commit()
        return True, 'Cópia deletada com sucesso!'
    except mysql.connector.Error as err:
        return False, f"Erro ao deletar cópia: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
