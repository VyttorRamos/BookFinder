import mysql.connector
from configDB import DBConexao

def BuscarConfiguracoes():
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configuracoes ORDER BY categoria, chave")
        configuracoes = cursor.fetchall()
        
        # Converter para dicionário mais fácil de usar
        config_dict = {}
        for config in configuracoes:
            config_dict[config['chave']] = {
                'valor': config['valor'],
                'descricao': config['descricao'],
                'categoria': config['categoria'],
                'id_config': config['id_config']
            }
        
        return True, config_dict
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar configurações: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def BuscarConfiguracaoPorChave(chave):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configuracoes WHERE chave = %s", (chave,))
        config = cursor.fetchone()
        
        if not config:
            return False, "Configuração não encontrada"
        
        return True, config
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar configuração: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarConfiguracao(id_config, valor):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE configuracoes SET valor = %s WHERE id_config = %s", (valor, id_config))
        conn.commit()
        return True, "Configuração atualizada com sucesso!"
    except mysql.connector.Error as err:
        return False, f"Erro ao atualizar configuração: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def AtualizarConfiguracoesEmLote(configuracoes_dict):
    try:
        conn = DBConexao()
        cursor = conn.cursor()
        
        for chave, valor in configuracoes_dict.items():
            cursor.execute("UPDATE configuracoes SET valor = %s WHERE chave = %s", (valor, chave))
        
        conn.commit()
        return True, "Configurações atualizadas com sucesso!"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Erro ao atualizar configurações: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def BuscarConfiguracoesPorCategoria(categoria):
    try:
        conn = DBConexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM configuracoes WHERE categoria = %s ORDER BY chave", (categoria,))
        configuracoes = cursor.fetchall()
        return True, configuracoes
    except mysql.connector.Error as err:
        return False, f"Erro ao buscar configurações: {err}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()