import os
import sys
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

# Adiciona o diretório pai ao path para importar modelos do backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emprestimoModel import ListarEmprestimosPorUsuario
from livroModel import ListarLivros

# Variáveis globais para manter o modelo na memória
MODELO_KNN = None
LIVROS_PIVOT = None
DADOS_CARREGADOS = False

def carregar_modelo():
    """
    Carrega os datasets e treina o modelo KNN.
    Executado apenas uma vez para não pesar o sistema.
    """
    global MODELO_KNN, LIVROS_PIVOT, DADOS_CARREGADOS
    
    if DADOS_CARREGADOS:
        return

    print("[IA] Iniciando carregamento do modelo de recomendação...")
    
    try:
        # Caminhos dos arquivos CSV (Ajuste se necessário)
        base_path = os.path.dirname(os.path.abspath(__file__))
        books_path = os.path.join(base_path, 'dataset', 'BX-Books.csv')
        ratings_path = os.path.join(base_path, 'dataset', 'BX-Book-Ratings.csv')

        # Verifica se arquivos existem
        if not os.path.exists(books_path) or not os.path.exists(ratings_path):
            print(f"[IA] Erro: Arquivos de dataset não encontrados em {base_path}/dataset/")
            return

        # --- 1. CARREGAMENTO (Baseado no seu script) ---
        livros = pd.read_csv(books_path, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)
        livros.columns = ['ISBN', 'TITULO', 'AUTOR', 'AnoPublicacao', 'Editora', 'URL_S', 'URL_M', 'URL_L']
        
        avaliacoes = pd.read_csv(ratings_path, sep=';', encoding='latin-1', on_bad_lines='skip')
        avaliacoes.columns = ['ID_USUARIO', 'ISBN', 'AVALIACAO']

        # --- 2. PRÉ-PROCESSAMENTO ---
        avaliacoes = avaliacoes[avaliacoes['AVALIACAO'] != 0] # Remove notas zero
        
        # Merge
        avaliacoes_e_livros = avaliacoes.merge(livros, on='ISBN')
        avaliacoes_e_livros.drop_duplicates(['ID_USUARIO', 'ISBN'], inplace=True)

        # --- 3. FILTRAGEM (Otimizada para performance web) ---
        # Reduzimos um pouco os thresholds para garantir que funcione com datasets menores de teste se necessário
        min_avaliacoes_livro = 50
        qt_avaliacoes_livro = avaliacoes_e_livros['TITULO'].value_counts()
        livros_selecionados = qt_avaliacoes_livro[qt_avaliacoes_livro >= min_avaliacoes_livro].index
        avaliacoes_filtradas = avaliacoes_e_livros[avaliacoes_e_livros['TITULO'].isin(livros_selecionados)]

        min_avaliacoes_usuario = 10
        qt_avaliacoes_usuario = avaliacoes_filtradas['ID_USUARIO'].value_counts()
        usuarios_selecionados = qt_avaliacoes_usuario[qt_avaliacoes_usuario >= min_avaliacoes_usuario].index
        avaliacoes_finais = avaliacoes_filtradas[avaliacoes_filtradas['ID_USUARIO'].isin(usuarios_selecionados)]

        # --- 4. PIVOT ---
        LIVROS_PIVOT = avaliacoes_finais.pivot_table(columns='ID_USUARIO', index='TITULO', values='AVALIACAO').fillna(0)

        # --- 5. TREINAMENTO ---
        livros_sparse = csr_matrix(LIVROS_PIVOT)
        MODELO_KNN = NearestNeighbors(metric='cosine', algorithm='brute')
        MODELO_KNN.fit(livros_sparse)

        DADOS_CARREGADOS = True
        print("[IA] Modelo KNN treinado com sucesso!")

    except Exception as e:
        print(f"[IA] Erro fatal ao treinar modelo: {e}")

def encontrar_titulo_similar(titulo_busca):
    """Tenta encontrar um título no dataset que seja parecido com o buscado"""
    if LIVROS_PIVOT is None: return None
    
    # 1. Tentativa exata
    for t in LIVROS_PIVOT.index:
        if t.lower() == titulo_busca.lower():
            return t
            
    # 2. Tentativa parcial (contém)
    for t in LIVROS_PIVOT.index:
        if titulo_busca.lower() in t.lower():
            return t
    
    return None

def obter_recomendacoes(id_usuario):
    """
    Lógica Principal:
    1. Pega o último livro que o usuário pegou emprestado no MySQL.
    2. Usa a IA para achar similares no dataset CSV.
    3. Tenta achar esses similares de volta no MySQL para exibir.
    """
    carregar_modelo()
    
    if not DADOS_CARREGADOS or MODELO_KNN is None:
        return []

    recomendacoes_finais = []
    
    try:
        # 1. Descobrir gosto do usuário (Último empréstimo)
        ok, emprestimos = ListarEmprestimosPorUsuario(id_usuario)
        
        if not ok or not emprestimos:
            return [] # Sem histórico, sem recomendação personalizada

        # Pega o título do último livro (assumindo que a lista vem ordenada ou pegamos o primeiro)
        ultimo_livro_titulo = emprestimos[0]['titulo']
        print(f"[IA] Buscando recomendações baseadas em: {ultimo_livro_titulo}")

        # 2. Buscar na IA
        titulo_dataset = encontrar_titulo_similar(ultimo_livro_titulo)
        
        titulos_sugeridos = []
        if titulo_dataset:
            # Lógica do seu script recomenda.py
            livro_linha = LIVROS_PIVOT.filter(items=[titulo_dataset], axis=0).values.reshape(1, -1)
            distances, suggestions = MODELO_KNN.kneighbors(livro_linha, n_neighbors=5)
            
            # Pega os títulos sugeridos (ignorando o primeiro que é o próprio livro)
            for i in range(1, len(suggestions.flatten())):
                idx = suggestions.flatten()[i]
                titulos_sugeridos.append(LIVROS_PIVOT.index[idx])
            
            print(f"[IA] A IA sugeriu: {titulos_sugeridos}")
        else:
            print(f"[IA] Livro '{ultimo_livro_titulo}' não encontrado no dataset de treinamento.")

        # 3. Cruzar com banco de dados local (MySQL)
        # Precisamos verificar se temos esses livros sugeridos no nosso acervo real
        if titulos_sugeridos:
            ok_db, todos_livros_db = ListarLivros()
            if ok_db:
                for sugerido in titulos_sugeridos:
                    for livro_db in todos_livros_db:
                        # Verifica se o título do banco está contido na sugestão ou vice-versa
                        if livro_db['titulo'].lower() in sugerido.lower() or sugerido.lower() in livro_db['titulo'].lower():
                            if livro_db not in recomendacoes_finais:
                                recomendacoes_finais.append(livro_db)
    
    except Exception as e:
        print(f"[IA] Erro ao gerar recomendações: {e}")
        return []

    return recomendacoes_finais