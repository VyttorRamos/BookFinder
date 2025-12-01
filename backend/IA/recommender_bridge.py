import os
import sys
import pandas as pd
import numpy as np
import random
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from difflib import SequenceMatcher  # Importante para comparar textos similares

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
        # Caminhos dos arquivos CSV
        base_path = os.path.dirname(os.path.abspath(__file__))
        books_path = os.path.join(base_path, 'dataset', 'BX-Books.csv')
        ratings_path = os.path.join(base_path, 'dataset', 'BX-Book-Ratings.csv')

        # Verifica se arquivos existem
        if not os.path.exists(books_path) or not os.path.exists(ratings_path):
            print(f"[IA] Erro: Arquivos de dataset não encontrados em {base_path}/dataset/")
            return

        # --- 1. CARREGAMENTO ---
        livros = pd.read_csv(books_path, sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)
        livros.columns = ['ISBN', 'TITULO', 'AUTOR', 'AnoPublicacao', 'Editora', 'URL_S', 'URL_M', 'URL_L']
        
        avaliacoes = pd.read_csv(ratings_path, sep=';', encoding='latin-1', on_bad_lines='skip')
        avaliacoes.columns = ['ID_USUARIO', 'ISBN', 'AVALIACAO']

        # --- 2. PRÉ-PROCESSAMENTO ---
        avaliacoes = avaliacoes[avaliacoes['AVALIACAO'] != 0] # Remove notas zero
        
        # Merge otimizado
        # Filtrando livros populares antes do merge para economizar memória
        min_avaliacoes_livro = 10  # Reduzi para 10 para captar mais livros em testes pequenos
        qt_avaliacoes = avaliacoes['ISBN'].value_counts()
        isbns_populares = qt_avaliacoes[qt_avaliacoes >= min_avaliacoes_livro].index
        avaliacoes = avaliacoes[avaliacoes['ISBN'].isin(isbns_populares)]

        avaliacoes_e_livros = avaliacoes.merge(livros, on='ISBN')
        avaliacoes_e_livros.drop_duplicates(['ID_USUARIO', 'ISBN'], inplace=True)

        # --- 3. PIVOT ---
        LIVROS_PIVOT = avaliacoes_e_livros.pivot_table(columns='ID_USUARIO', index='TITULO', values='AVALIACAO').fillna(0)

        # --- 4. TREINAMENTO ---
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
    if titulo_busca in LIVROS_PIVOT.index:
        return titulo_busca
            
    # 2. Tentativa parcial (contém)
    for t in LIVROS_PIVOT.index:
        if titulo_busca.lower() in t.lower():
            return t
    
    return None

def obter_recomendacoes(id_usuario):
    """
    Lógica Principal com Fallback (Plano B):
    1. Tenta recomendar via IA (KNN).
    2. Se falhar ou não achar livros correspondentes, retorna livros aleatórios do banco.
    """
    carregar_modelo()
    
    recomendacoes_finais = []
    
    # Busca todos os livros do banco local (MySQL) para cruzamento ou fallback
    ok_db, todos_livros_db = ListarLivros()
    if not ok_db: todos_livros_db = []

    try:
        # --- ETAPA 1: TENTATIVA IA ---
        sucesso_ia = False
        
        # Verifica se temos o modelo carregado
        if DADOS_CARREGADOS and MODELO_KNN is not None:
            ok, emprestimos = ListarEmprestimosPorUsuario(id_usuario)
            
            if ok and emprestimos:
                ultimo_livro_titulo = emprestimos[0]['titulo']
                print(f"[IA] Baseando-se em: {ultimo_livro_titulo}")

                titulo_dataset = encontrar_titulo_similar(ultimo_livro_titulo)
                
                if titulo_dataset:
                    livro_linha = LIVROS_PIVOT.filter(items=[titulo_dataset], axis=0).values.reshape(1, -1)
                    distances, suggestions = MODELO_KNN.kneighbors(livro_linha, n_neighbors=6)
                    
                    titulos_sugeridos = []
                    for i in range(1, len(suggestions.flatten())):
                        idx = suggestions.flatten()[i]
                        titulos_sugeridos.append(LIVROS_PIVOT.index[idx])
                    
                    print(f"[IA] Sugestões brutas: {titulos_sugeridos}")

                    # Cruzamento inteligente com difflib
                    for sugerido in titulos_sugeridos:
                        for livro_db in todos_livros_db:
                            # Calcula similaridade (0 a 1)
                            ratio = SequenceMatcher(None, livro_db['titulo'].lower(), sugerido.lower()).ratio()
                            
                            # Se for mais de 50% similar, considera match
                            if ratio > 0.5:
                                if livro_db not in recomendacoes_finais:
                                    recomendacoes_finais.append(livro_db)
                                    sucesso_ia = True
                else:
                    print(f"[IA] Título '{ultimo_livro_titulo}' não consta no dataset de treino.")
        
        # --- ETAPA 2: FALLBACK (PLANO B) ---
        # Se a lista estiver vazia (seja por erro, falta de histórico, ou falta de match no acervo)
        if not recomendacoes_finais:
            print("[IA] Sem matches exatos. Ativando modo Fallback (Aleatório)...")
            
            # Removemos duplicatas e garantimos que existem livros
            if todos_livros_db:
                qtd = min(4, len(todos_livros_db))
                recomendacoes_finais = random.sample(todos_livros_db, qtd)

    except Exception as e:
        print(f"[IA] Erro ao gerar recomendações: {e}")
        # Última tentativa de salvar a UX
        if todos_livros_db:
            recomendacoes_finais = random.sample(todos_livros_db, min(4, len(todos_livros_db)))

    return recomendacoes_finais