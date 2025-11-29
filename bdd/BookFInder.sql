CREATE DATABASE BookFinderDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE BookFinderDB;
select *from usuarios;

-- Tabela dos usuários do sistema (PRIMEIRO - não depende de ninguém)
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, 
    telefone VARCHAR(20),
    tipo_usuario ENUM('aluno', 'professor', 'admin', 'bibliotecario') DEFAULT 'aluno',
    status_usuario ENUM('ativo', 'inativo') DEFAULT 'ativo',
    dt_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    dt_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela dos autores (SEGUNDO - não depende de ninguém)
CREATE TABLE autores (
    id_autor INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    biografia TEXT NULL
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela das editoras (TERCEIRO - não depende de ninguém)
CREATE TABLE editoras (
    id_editora INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco VARCHAR(255) NULL,
    telefone VARCHAR(20) NULL,
    email VARCHAR(255) NULL
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela das categorias (QUARTO - não depende de ninguém)
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT NULL
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela dos livros (QUINTO - depende de editoras e categorias)
CREATE TABLE livros (
    id_livro INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    ano_publicacao YEAR,
    id_editora INT NOT NULL,
    id_categoria INT NOT NULL,
    status_livro ENUM('ativo', 'removido', 'manutencao') DEFAULT 'ativo',
    dt_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    dt_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_livros_editora FOREIGN KEY (id_editora) REFERENCES editoras(id_editora) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_livros_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de relacionamento N:N entre livros e autores (SEXTO - depende de livros e autores)
CREATE TABLE livros_autores (
    id_livro INT NOT NULL,
    id_autor INT NOT NULL,
    PRIMARY KEY (id_livro, id_autor),
    CONSTRAINT fk_la_livro FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_la_autor FOREIGN KEY (id_autor) REFERENCES autores(id_autor) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de Tags (SÉTIMO - não depende de ninguém)
CREATE TABLE tags (
	id_tag INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) UNIQUE NOT NULL
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de relacionamento N:N entre livros e tags (OITAVO - depende de livros e tags)
CREATE TABLE livros_tags (
	id_livro INT NOT NULL,
    id_tag INT NOT NULL,
    PRIMARY KEY (id_livro, id_tag),
    CONSTRAINT fk_lt_livro FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_lt_tag FOREIGN KEY (id_tag) REFERENCES tags(id_tag) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de exemplares (cópias físicas) (NONO - depende de livros)
CREATE TABLE copias (
    id_copia INT AUTO_INCREMENT PRIMARY KEY,
    id_livro INT NOT NULL,
    cod_interno VARCHAR(100) UNIQUE NOT NULL,
    status_copia ENUM('disponivel', 'emprestado', 'danificado', 'perdido') DEFAULT 'disponivel',
    CONSTRAINT fk_copias_livro FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de empréstimos (DÉCIMO - depende de usuarios e copias)
CREATE TABLE emprestimos (
    id_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_copia INT NOT NULL,
    dt_emprestimo DATETIME DEFAULT CURRENT_TIMESTAMP,
    dt_prevista_devolucao DATETIME NOT NULL,
    dt_devolucao DATETIME NULL,
    status_emprestimo ENUM('ativo', 'devolvido', 'atrasado', 'cancelado') DEFAULT 'ativo',
    obs TEXT NULL,
    CONSTRAINT fk_emprestimos_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_emprestimos_copia FOREIGN KEY (id_copia) REFERENCES copias(id_copia) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de multas (DÉCIMO PRIMEIRO - depende de emprestimos)
CREATE TABLE multas (
    id_multa INT AUTO_INCREMENT PRIMARY KEY,
    id_emprestimo INT NOT NULL,
    valor DECIMAL(8, 2) NOT NULL,
    status_multa ENUM('pendente', 'pago', 'cancelado') DEFAULT 'pendente',
    dt_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    dt_pagamento DATETIME NULL,
    CONSTRAINT fk_multas_emprestimo FOREIGN KEY (id_emprestimo) REFERENCES emprestimos(id_emprestimo) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de Recomendações (DÉCIMO SEGUNDO - depende de usuarios e livros)
CREATE TABLE recomendacoes (
    id_recomendacao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_livro INT NOT NULL,
    motivo TEXT NULL,
    dt_recomendacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recomendacoes_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_recomendacoes_livro FOREIGN KEY (id_livro) REFERENCES livros(id_livro) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Tabela de histórico de ações (DÉCIMO TERCEIRO - depende de usuarios)
CREATE TABLE hist_acoes (
    id_acao INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    acao VARCHAR(255) NOT NULL,
    ip VARCHAR(50),
    dt_acao DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_histAcoes_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;


-- Atualização no banco:
-- Adicionar colunas de quantidade nos livros
ALTER TABLE livros 
ADD COLUMN quantidade_total INT DEFAULT 1,
ADD COLUMN quantidade_disponivel INT DEFAULT 1;

-- Adicionar coluna de renovação nos empréstimos
ALTER TABLE emprestimos 
ADD COLUMN renovado BOOLEAN DEFAULT FALSE;

-- Adicionar colunas adicionais nas multas
ALTER TABLE multas 
ADD COLUMN dias_atraso INT NULL,
ADD COLUMN id_usuario INT NULL;

-- Atualizar a foreign key da multa para usuário
ALTER TABLE multas 
ADD CONSTRAINT fk_multas_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario);

-- Atualizar livros existentes
UPDATE livros SET quantidade_total = 1, quantidade_disponivel = 1 
WHERE quantidade_total IS NULL OR quantidade_disponivel IS NULL limit 1;

CREATE TABLE configuracoes (
    id_config INT AUTO_INCREMENT PRIMARY KEY,
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor VARCHAR(255) NOT NULL,
    descricao TEXT,
    categoria VARCHAR(50) DEFAULT 'geral',
    dt_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    dt_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Inserir configurações padrão
INSERT INTO configuracoes (chave, valor, descricao, categoria) VALUES
('multa_por_dia', '2.00', 'Valor da multa por dia de atraso (R$)', 'multas'),
('limite_emprestimos', '3', 'Número máximo de empréstimos por usuário', 'emprestimos'),
('prazo_aluno', '15', 'Prazo de empréstimo para alunos (dias)', 'emprestimos'),
('prazo_professor', '30', 'Prazo de empréstimo para professores (dias)', 'emprestimos'),
('limite_renovacoes', '1', 'Número máximo de renovações por empréstimo', 'emprestimos'),
('dias_renovacao', '15', 'Dias adicionais ao renovar empréstimo', 'emprestimos');