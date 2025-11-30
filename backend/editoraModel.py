import mysql.connector
from configDB import DBConexao

def ListarEditoras():
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM editoras ORDER BY nome")
        editoras = cursor.fetchall()
        return True, editoras
    except mysql.connector.Error as err:
        return False, f"Erro ao listar editoras: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao listar editoras: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def CadastrarEditora(nome, endereco=None, telefone=None, email=None):
    # Validação básica antes de tentar conectar
    if not nome:
        return False, "O nome da editora é obrigatório!"

    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO editoras (nome, endereco, telefone, email) 
            VALUES (%s, %s, %s, %s)
        """, (nome, endereco, telefone, email))
        conn.commit()
        return True, "Editora cadastrada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao cadastrar editora: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao cadastrar editora: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def PegaEditoraPorId(id_editora):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM editoras WHERE id_editora = %s", (id_editora,))
        editora = cursor.fetchone()
        if not editora:
            return False, "Editora não encontrada."
        return True, editora
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar editora: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao buscar editora: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def AtualizarEditora(id_editora, nome, endereco=None, telefone=None, email=None):
    if not nome:
        return False, "O nome da editora é obrigatório!"

    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE editoras 
            SET nome = %s, endereco = %s, telefone = %s, email = %s 
            WHERE id_editora = %s
        """, (nome, endereco, telefone, email, id_editora))
        conn.commit()
        return True, "Editora atualizada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar editora: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao atualizar editora: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def DeletarEditora(id_editora):
    conn = None
    cursor = None
    try:
        conn = DBConexao()
        if conn is None:
            return False, "Erro: Não foi possível conectar ao banco de dados"
        
        cursor = conn.cursor()
        
        # Verificar se a editora está sendo usada em algum livro
        cursor.execute("SELECT * FROM livros WHERE id_editora = %s", (id_editora,))
        if cursor.fetchone():
            return False, "Não é possível excluir a editora, pois existem livros associados a ela."
            
        cursor.execute("DELETE FROM editoras WHERE id_editora = %s", (id_editora,))
        conn.commit()
        return True, "Editora deletada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao deletar editora: {err}"
    except Exception as e:
        return False, f"Erro inesperado ao deletar editora: {e}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()