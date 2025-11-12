# Importando os pacotes que vão ser utilizados
import pandas as pd
import numpy as np
import sys # Para encerrar o programa se o arquivo não for encontrado
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

# Inicializando DataFrames como None
livros = None
avaliacoes = None

# --- 1. CARREGAMENTO DOS DATASETS IDEAIS (Book-Crossing) ---
# Tenta carregar os arquivos e encerra o programa se falhar

try:
    # 1.1 Carregando Livros
    print("Tentando carregar BX-Books.csv...")
    # Rota corrigida: 'dataset/BX-Books.csv'
    livros = pd.read_csv('dataset/BX-Books.csv', sep=';', encoding='latin-1', on_bad_lines='skip', low_memory=False)
    livros.columns = ['ISBN', 'TITULO', 'AUTOR', 'AnoPublicacao', 'Editora', 'URL_S', 'URL_M', 'URL_L']
    print("Livros carregados com sucesso.")
    print(livros.head(3))

    # 1.2 Carregando Avaliações
    print("\nTentando carregar BX-Book-Ratings.csv...")
    # Rota corrigida: 'dataset/BX-Book-Ratings.csv'
    avaliacoes = pd.read_csv('dataset/BX-Book-Ratings.csv', sep=';', encoding='latin-1', on_bad_lines='skip')
    avaliacoes.columns = ['ID_USUARIO', 'ISBN', 'AVALIACAO']
    print("Avaliações carregadas com sucesso.")
    print(avaliacoes.head())

except FileNotFoundError as e:
    print(f"\n--- ERRO CRÍTICO: ARQUIVO NÃO ENCONTRADO ---")
    print(f"O arquivo {e.filename} não foi encontrado.")
    print("✅ Ação Necessária: Certifique-se de que 'BX-Books.csv' e 'BX-Book-Ratings.csv' estão dentro da pasta 'dataset/' em relação ao script.")
    sys.exit(1) # Encerra o programa se os arquivos não forem carregados


# --- 2. PRÉ-PROCESSAMENTO DE DADOS E FILTRAGEM ---
# Agora que sabemos que 'avaliacoes' existe, podemos prosseguir

# Verificando se há valores nulos nos dados que serão utilizados
print("\nValores nulos (Avaliações):")
# Usamos .loc para evitar o Warning de SettingWithCopy
print(avaliacoes.loc[:, ['ID_USUARIO', 'ISBN', 'AVALIACAO']].isna().sum())

# Filtragem Crucial: Remover avaliações implícitas (Nota 0)
avaliacoes_expl = avaliacoes[avaliacoes['AVALIACAO'] != 0].copy()
print(f"\nShape após remover avaliações implícitas (Nota 0): {avaliacoes_expl.shape}")


# Concatenando os dataframes
avaliacoes_e_livros = avaliacoes_expl.merge(livros, on='ISBN')

# Descartar valores duplicados (Usuário X Livro)
avaliacoes_e_livros.drop_duplicates(['ID_USUARIO', 'ISBN'], inplace=True)
print(f"Shape após remover duplicatas: {avaliacoes_e_livros.shape}")


# --- 3. FILTRAGEM DE RUÍDO (Usuários e Livros com poucas interações) ---

# 3.1 Filtrar Livros: Manter apenas livros com mais de 50 avaliações
min_avaliacoes_livro = 50
qt_avaliacoes_livro = avaliacoes_e_livros['TITULO'].value_counts()
livros_selecionados = qt_avaliacoes_livro[qt_avaliacoes_livro >= min_avaliacoes_livro].index
avaliacoes_filtradas = avaliacoes_e_livros[avaliacoes_e_livros['TITULO'].isin(livros_selecionados)].copy()

print(f"\nShape após filtrar livros (>{min_avaliacoes_livro} avaliações): {avaliacoes_filtradas.shape}")


# 3.2 Filtrar Usuários: Manter apenas usuários que avaliaram mais de 10 livros
min_avaliacoes_usuario = 10
qt_avaliacoes_usuario = avaliacoes_filtradas['ID_USUARIO'].value_counts()
usuarios_selecionados = qt_avaliacoes_usuario[qt_avaliacoes_usuario >= min_avaliacoes_usuario].index
avaliacoes_finais = avaliacoes_filtradas[avaliacoes_filtradas['ID_USUARIO'].isin(usuarios_selecionados)].copy()

print(f"Shape FINAL após filtrar usuários (>{min_avaliacoes_usuario} avaliações): {avaliacoes_finais.shape}")


# --- 4. CRIAÇÃO DA MATRIZ USUÁRIO-ITEM (PIVOT) ---

# Fazendo o PIVOT: (Linha: TITULO, Coluna: ID_USUARIO, Valor: AVALIACAO)
livros_pivot = avaliacoes_finais.pivot_table(columns='ID_USUARIO', index='TITULO', values='AVALIACAO')

# Os valores que são nulos (onde o usuário não avaliou o livro) iremos preencher com ZERO
livros_pivot.fillna(0, inplace=True)
print("\nMatriz Pivot (Usuário x Livro) - Amostra:")
print(livros_pivot.head(5))


# --- 5. TREINAMENTO DO MODELO KNN ---

# Transformar o dataset em uma matriz sparsa (eficiente para matrizes com muitos zeros)
livros_sparse = csr_matrix(livros_pivot)

# Criando e treinando o modelo preditivo (KNN baseado na similaridade de cosseno)
modelo = NearestNeighbors(metric='cosine', algorithm='brute')
modelo.fit(livros_sparse)

print("\nModelo KNN de Filtragem Colaborativa treinado.")

# --- 6. AVALIAÇÃO E SUGESTÃO DE LIVROS ---

# Função auxiliar para fazer a sugestão
def sugerir_livros(titulo_livro, pivot_df, modelo_knn, k=6):

    # Normalizando o título para lidar com maiúsculas/minúsculas e variações (busca por correspondência exata)
    try:
        # Encontra o título exato na matriz pivot, ignorando a caixa
        titulo_exato = [t for t in pivot_df.index if t.lower() == titulo_livro.lower()][0]

        # Pega a linha do livro e transforma para o formato que o modelo espera
        livro_linha = pivot_df.filter(items=[titulo_exato], axis=0).values.reshape(1, -1)

        # Encontra as distâncias (similaridade) e os índices dos vizinhos
        distances, suggestions = modelo_knn.kneighbors(livro_linha, n_neighbors=k)

        print(f"\nRecomendações para o livro: '{titulo_exato}'")
        print("-" * 30)
        # Itera sobre os índices e exibe os títulos dos livros (excluindo o primeiro, que é o próprio livro)
        for i in range(1, len(suggestions.flatten())):
            distancia = distances.flatten()[i]
            # Similaridade é 1 - Distância (Cosseno)
            print(f"  {i}. {pivot_df.index[suggestions.flatten()[i]]} (Similaridade: {1-distancia:.3f})")

    except IndexError:
        print(f"\nLivro '{titulo_livro}' não encontrado na matriz final. Tente outro título exato.")


# --- Testando Recomendações (Títulos em caixa baixa para facilitar o teste) ---
# Atenção: Use títulos que você sabe que estão no dataset final filtrado.
sugerir_livros('The Two Towers (The Lord of the Rings, Part 2)', livros_pivot, modelo)
sugerir_livros('The Da Vinci Code', livros_pivot, modelo)
sugerir_livros('The Giver (Giver Quartet)', livros_pivot, modelo)