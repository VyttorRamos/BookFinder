from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from datetime import timedelta
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import random
import requests

# Importação dos modelos
from userModel import (CadastroUser, PegaUserPorEmail, VerificaLoginUsuario, ListarUsuarios, PegaUserPorId, AtualizarUsuario, DeletarUsuario)
from livroModel import (ListarLivros, CadastrarLivro, PegaLivroPorId, AtualizarLivro, DeletarLivro)
from generoModel import (ListarGeneros, CadastrarGenero, PegaGeneroPorId, AtualizarGenero, DeletarGenero)
from emprestimoModel import (ListarEmprestimos, RealizarEmprestimo, PegaEmprestimoPorId, RenovarEmprestimo, DevolverLivro, ListarAtrasados)
from multaModel import (ListarMultas, PegaMultaPorId, RemoverMulta)
from editoraModel import (ListarEditoras, CadastrarEditora, PegaEditoraPorId, AtualizarEditora, DeletarEditora)


load_dotenv()

app = Flask(__name__)

# Configurações
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "keysecret")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secretkey")
AcessoExpirado = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
RefreshExpirado = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=AcessoExpirado)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=RefreshExpirado)

jwt = JWTManager(app)

CORS(app)



@app.route("/buscar-livros")
def buscar_livros():
    """Página simples de busca na API do Google Books"""
    return render_template('buscar_livros.html')

@app.route("/api/buscar-livros")
def api_buscar_livros():
    """API que busca livros no Google Books"""
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({"error": "Digite um termo para busca"}), 400
    
    try:
        # API do Google Books (não precisa de chave!)
        url = f"https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': termo,
            'maxResults': 12,  # Limite de resultados
            'langRestrict': 'pt'  # Livros em português
        }
        
        response = requests.get(url, params=params, timeout=10)
        dados = response.json()
        
        livros = []
        for item in dados.get('items', []):
            info = item.get('volumeInfo', {})
            livro = {
                'id': item.get('id'),
                'titulo': info.get('title', 'Título não disponível'),
                'autores': ', '.join(info.get('authors', ['Autor desconhecido'])),
                'editora': info.get('publisher', 'Editora não informada'),
                'ano': info.get('publishedDate', '')[:4] if info.get('publishedDate') else 'N/A',
                'descricao': info.get('description', 'Descrição não disponível.'),
                'capa': info.get('imageLinks', {}).get('thumbnail', ''),
                'link': info.get('infoLink', '#')
            }
            livros.append(livro)
        
        return jsonify({"livros": livros})
        
    except Exception as e:
        return jsonify({"error": f"Erro na busca: {str(e)}"}), 500


@app.route("/api/listar-livros")
def api_listar_livros():
    """Retorna os livros do banco em JSON"""
    ok, livros = ListarLivros()
    if not ok:
        return jsonify({"error": livros}), 500

    # Normalizar campos mínimos esperados pelo frontend
    out = []
    for l in livros:
        out.append({
            "id": l.get("id_livro"),
            "titulo": l.get("titulo"),
            "autor": l.get("autor") or l.get("editora_nome") or '',
            "categoria": l.get("categoria_nome") or l.get("nome_genero") or '',
            "ano": l.get("ano_publicacao") or '',
            "capa": l.get("capa") if l.get("capa") else ''
        })

    return jsonify({"livros": out}), 200


@app.route('/api/livros', methods=['GET', 'POST'])
def api_livros():
    if request.method == 'GET':
        ok, livros = ListarLivros()
        if not ok:
            return jsonify({'error': livros}), 500
        out = []
        for l in livros:
            out.append({
                'id': l.get('id_livro'),
                'titulo': l.get('titulo'),
                'autor': l.get('autor') or '',
                'categoria': l.get('categoria_nome') or '',
                'ano': l.get('ano_publicacao') or '',
                'capa': l.get('capa') if l.get('capa') else ''
            })
        return jsonify({'livros': out}), 200

    # POST - criar livro (espera JSON)
    data = request.get_json() or {}
    titulo = data.get('titulo')
    isbn = data.get('isbn')
    ano_publicacao = data.get('ano_publicacao')
    id_editora = data.get('id_editora')
    id_categoria = data.get('id_categoria')

    if not titulo:
        return jsonify({'error': 'titulo é obrigatório'}), 400

    ok, res = CadastrarLivro(titulo, isbn, ano_publicacao, id_editora, id_categoria)
    if not ok:
        return jsonify({'error': res}), 500

    return jsonify({'message': res}), 201


@app.route('/api/livros/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_livro_detail(id):
    if request.method == 'GET':
        ok, livro = PegaLivroPorId(id)
        if not ok:
            return jsonify({'error': livro}), 404
        out = {
            'id': livro.get('id_livro'),
            'titulo': livro.get('titulo'),
            'isbn': livro.get('isbn'),
            'ano': livro.get('ano_publicacao'),
            'id_editora': livro.get('id_editora'),
            'id_categoria': livro.get('id_categoria'),
            'autor': livro.get('autor') or '',
            'categoria': livro.get('categoria_nome') or '',
            'capa': livro.get('capa') if livro.get('capa') else ''
        }
        return jsonify(out), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        titulo = data.get('titulo')
        isbn = data.get('isbn')
        ano_publicacao = data.get('ano_publicacao')
        id_editora = data.get('id_editora')
        id_categoria = data.get('id_categoria')

        if not titulo:
            return jsonify({'error': 'titulo é obrigatório'}), 400

        ok, res = AtualizarLivro(id, titulo, isbn, ano_publicacao, id_editora, id_categoria)
        if not ok:
            return jsonify({'error': res}), 500
        return jsonify({'message': res}), 200

    # DELETE
    ok, res = DeletarLivro(id)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 200

# Função para gerar CAPTCHA
def gerar_captcha():
    operadores = ['+', '-', '*']
    operador = random.choice(operadores)
    
    # Garantir que os números sejam sempre inteiros e a operação seja clara
    if operador == '+':
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        resposta = num1 + num2
    elif operador == '-':
        num1 = random.randint(10, 30)
        num2 = random.randint(1, num1 - 1)  # Garante resultado positivo
        resposta = num1 - num2
    else:  # multiplicação
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 5)
        resposta = num1 * num2
    
    print(f"DEBUG CAPTCHA: {num1} {operador} {num2} = {resposta}")
    return num1, num2, operador, resposta

# --- ROTAS HTML ---
@app.route("/")
def home():
    """Página inicial com livros do banco de dados"""
    # Buscar os últimos livros cadastrados
    ok, livros = ListarLivros()
    
    # Buscar usuários para o empréstimo
    ok_usuarios, usuarios = ListarUsuarios()
    
    # Se der erro, mostra página sem livros
    if not ok:
        livros = []
    if not ok_usuarios:
        usuarios = []
    
    # Pegar apenas os primeiros 8 livros para exibir
    livros_destaque = livros[:8] if livros else []
    
    return render_template('index.html', 
                         livros=livros_destaque, 
                         usuarios=usuarios)

@app.route("/generos")
def generos():
    return render_template('generos.html')

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

@app.route("/contato")
def contato():
    return render_template('contato.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # --- Verificação do CAPTCHA ---
        captcha_resposta_usuario = request.form.get("notrobo", "").strip()
        captcha_resposta_correta = request.form.get("captcha_correta", "").strip()
        
        print(f"DEBUG: Resposta usuário: {captcha_resposta_usuario}")
        print(f"DEBUG: Resposta correta esperada: {captcha_resposta_correta}")
        
        if not captcha_resposta_usuario or captcha_resposta_usuario != captcha_resposta_correta:
            # CAPTCHA incorreto → gerar novo
            num1, num2, operador, resposta = gerar_captcha()
            
            return render_template(
                "login.html",
                error="Resposta do CAPTCHA incorreta. Tente novamente.",
                captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
                captcha_correta=resposta,
                email=request.form.get('email', '')
            )

        # --- CAPTCHA correto: verificar login ---
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        ok, res = VerificaLoginUsuario(email, senha)
        if not ok:
            # Login falhou → gerar novo CAPTCHA
            num1, num2, operador, resposta = gerar_captcha()
            
            return render_template(
                "login.html",
                error=res,
                captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
                captcha_correta=resposta,
                email=email
            )

        # --- Login bem-sucedido ---
        usuario = PegaUserPorEmail(email)

        # Redirecionar conforme tipo de usuário
        if usuario["tipo_usuario"].lower() == "admin":
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("home"))

    # --- GET: exibe login com novo CAPTCHA ---
    num1, num2, operador, resposta = gerar_captcha()
    
    print(f"DEBUG: Novo CAPTCHA gerado - Pergunta: {num1} {operador} {num2}, Resposta: {resposta}")
    
    return render_template(
        "login.html",
        captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
        captcha_correta=resposta
    )

@app.route("/logout")
def logout():
    return redirect(url_for('home'))

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/privacidade")
def privacidade():
    return render_template('privacidade.html')

@app.route("/termos")
def termos():
    return render_template('termos.html')

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

# ---------------- USUÁRIOS ----------------
@app.route("/listaruser")
def listaruser():
    ok, usuarios = ListarUsuarios()
    if not ok:
        return render_template('error.html', message=usuarios)
    return render_template('usuarios/listaruser.html', usuarios=usuarios)

@app.route("/editaruser/<int:id>")
def editaruser(id):
    ok, usuario = PegaUserPorId(id)
    if not ok:
        return render_template('error.html', message=usuario)
    return render_template('usuarios/editaruser.html', usuario=usuario)

@app.route("/update_user/<int:id>", methods=["POST"])
def update_user(id):
    nome_completo = request.form['nome_completo']
    email = request.form['email']
    telefone = request.form['telefone']
    tipo_usuario = request.form['tipo_usuario']
    ok, message = AtualizarUsuario(id, nome_completo, email, telefone, tipo_usuario)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listaruser'))

@app.route("/excluiruser/<int:id>")
def excluiruser(id):
    ok, usuario = PegaUserPorId(id)
    if not ok:
        return render_template('error.html', message=usuario)
    return render_template('usuarios/excluiruser.html', usuario=usuario)

@app.route("/delete_user/<int:id>", methods=["POST"])
def delete_user(id):
    ok, message = DeletarUsuario(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listaruser'))

# ---------------- EDITORAS ----------------
@app.route("/listareditoras")
def listareditoras():
    ok, editoras = ListarEditoras()
    if not ok:
        return render_template('error.html', message=editoras)
    return render_template('editoras/listareditoras.html', editoras=editoras)

@app.route("/cadastrareditora", methods=["GET", "POST"])
def cadastrareditora():
    if request.method == "POST":
        nome = request.form['nome'].strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not nome:
            return render_template('editoras/cadastrareditora.html', 
                                 error="Nome da editora é obrigatório")
        
        ok, message = CadastrarEditora(nome, endereco, telefone, email)
        if not ok:
            return render_template('editoras/cadastrareditora.html', 
                                 error=message, nome=nome, endereco=endereco, 
                                 telefone=telefone, email=email)
        
        return redirect(url_for('listareditoras'))
    
    return render_template('editoras/cadastrareditora.html')

@app.route("/editareditora/<int:id>", methods=["GET", "POST"])
def editareditora(id):
    if request.method == "POST":
        nome = request.form['nome'].strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not nome:
            ok, editora = PegaEditoraPorId(id)
            if not ok:
                return render_template('error.html', message=editora)
            return render_template('editoras/editareditora.html', 
                                 editora=editora, error="Nome da editora é obrigatório")
        
        ok, message = AtualizarEditora(id, nome, endereco, telefone, email)
        if not ok:
            ok, editora = PegaEditoraPorId(id)
            if not ok:
                return render_template('error.html', message=editora)
            return render_template('editoras/editareditora.html', 
                                 editora=editora, error=message)
        
        return redirect(url_for('listareditoras'))
    
    # GET - Carregar dados da editora
    ok, editora = PegaEditoraPorId(id)
    if not ok:
        return render_template('error.html', message=editora)
    
    return render_template('editoras/editareditora.html', editora=editora)

@app.route("/update_editora/<int:id>", methods=["POST"])
def update_editora(id):
    nome = request.form['nome'].strip()
    endereco = request.form.get('endereco', '').strip()
    telefone = request.form.get('telefone', '').strip()
    email = request.form.get('email', '').strip()
    
    if not nome:
        return render_template('error.html', message="Nome da editora é obrigatório")
    
    ok, message = AtualizarEditora(id, nome, endereco, telefone, email)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listareditoras'))

@app.route("/excluireditora/<int:id>")
def excluireditora(id):
    ok, editora = PegaEditoraPorId(id)
    if not ok:
        return render_template('error.html', message=editora)
    
    return render_template('editoras/excluireditora.html', editora=editora)

@app.route("/delete_editora/<int:id>", methods=["POST"])
def delete_editora(id):
    ok, message = DeletarEditora(id)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listareditoras'))

# ---------------- LIVROS ----------------
@app.route("/listarlivro")
def listarlivros():
    ok, livros = ListarLivros()
    if not ok:
        return render_template('error.html', message=livros)
    return render_template('livros/listarlivro.html', livros=livros)

@app.route("/cadastrarlivro", methods=["GET", "POST"])
def cadastrarlivro():
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        isbn = request.form.get('isbn', '').strip()
        ano_publicacao = request.form.get('ano_publicacao', '').strip()
        id_editora = request.form.get('id_editora')
        id_categoria = request.form.get('id_categoria')
        
        if not titulo:
            return render_template('livros/cadastrarlivro.html', 
                                 error="Título do livro é obrigatório")
        
        ok, message = CadastrarLivro(titulo, isbn, ano_publicacao, id_editora, id_categoria)
        if not ok:
            return render_template('livros/cadastrarlivro.html', 
                                 error=message, titulo=titulo, isbn=isbn, 
                                 ano_publicacao=ano_publicacao)
        
        return redirect(url_for('listarlivros'))
    
    return render_template('livros/cadastrarlivro.html')

@app.route("/editarlivro/<int:id>", methods=["GET", "POST"])
def editarlivro(id):
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        isbn = request.form.get('isbn', '').strip()
        ano_publicacao = request.form.get('ano_publicacao', '').strip()
        id_editora = request.form.get('id_editora')
        id_categoria = request.form.get('id_categoria')
        
        if not titulo:
            ok, livro = PegaLivroPorId(id)
            if not ok:
                return render_template('error.html', message=livro)
            return render_template('livros/editarlivro.html', 
                                 livro=livro, error="Título do livro é obrigatório")
        
        ok, message = AtualizarLivro(id, titulo, isbn, ano_publicacao, id_editora, id_categoria)
        if not ok:
            ok, livro = PegaLivroPorId(id)
            if not ok:
                return render_template('error.html', message=livro)
            return render_template('livros/editarlivro.html', 
                                 livro=livro, error=message)
        
        return redirect(url_for('listarlivros'))
    
    # GET - Carregar dados do livro
    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    
    return render_template('livros/editarlivro.html', livro=livro)

# ADICIONE ESTA ROTA FALTANTE
@app.route("/update_livro/<int:id>", methods=["POST"])
def update_livro(id):
    titulo = request.form['titulo'].strip()
    isbn = request.form.get('isbn', '').strip()
    ano_publicacao = request.form.get('ano_publicacao', '').strip()
    id_editora = request.form.get('id_editora')
    id_categoria = request.form.get('id_categoria')
    
    if not titulo:
        return render_template('error.html', message="Título do livro é obrigatório")
    
    ok, message = AtualizarLivro(id, titulo, isbn, ano_publicacao, id_editora, id_categoria)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listarlivros'))

@app.route("/excluirlivro/<int:id>", methods=["GET", "POST"])
def excluirlivro(id):
    if request.method == 'POST':
        ok, message = DeletarLivro(id)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listarlivros'))

    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    return render_template('livros/excluirlivro.html', livro=livro)

# ADICIONE ESTA ROTA FALTANTE
@app.route("/delete_livro/<int:id>", methods=["POST"])
def delete_livro(id):
    ok, message = DeletarLivro(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listarlivros'))

# ---------------- GÊNEROS ----------------
@app.route("/listargeneros")
def listargeneros():
    ok, generos = ListarGeneros()
    if not ok:
        return render_template('error.html', message=generos)
    return render_template('generos/listargeneros.html', generos=generos)

@app.route("/cadastrargenero", methods=["GET", "POST"])
def cadastrargenero():
    if request.method == "POST":
        nome_genero = request.form['nome_genero'].strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome_genero:
            return render_template('generos/cadastrargenero.html', 
                                 error="Nome da categoria é obrigatório")
        
        ok, message = CadastrarGenero(nome_genero, descricao)
        if not ok:
            return render_template('generos/cadastrargenero.html', 
                                 error=message, nome_genero=nome_genero, descricao=descricao)
        
        return redirect(url_for('listargeneros'))
    
    return render_template('generos/cadastrargenero.html')

@app.route("/editargenero/<int:id>", methods=["GET", "POST"])
def editargenero(id):
    if request.method == "POST":
        nome_genero = request.form['nome_genero'].strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome_genero:
            ok, genero = PegaGeneroPorId(id)
            if not ok:
                return render_template('error.html', message=genero)
            return render_template('generos/editargenero.html', 
                                 genero=genero, error="Nome da categoria é obrigatório")
        
        ok, message = AtualizarGenero(id, nome_genero, descricao)
        if not ok:
            ok, genero = PegaGeneroPorId(id)
            if not ok:
                return render_template('error.html', message=genero)
            return render_template('generos/editargenero.html', 
                                 genero=genero, error=message)
        
        return redirect(url_for('listargeneros'))
    
    # GET - Carregar dados do gênero
    ok, genero = PegaGeneroPorId(id)
    if not ok:
        return render_template('error.html', message=genero)
    
    return render_template('generos/editargenero.html', genero=genero)

@app.route("/update_genero/<int:id>", methods=["POST"])
def update_genero(id):
    nome_genero = request.form['nome_genero'].strip()
    descricao = request.form.get('descricao', '').strip()
    
    if not nome_genero:
        return render_template('error.html', message="Nome da categoria é obrigatório")
    
    ok, message = AtualizarGenero(id, nome_genero, descricao)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listargeneros'))

@app.route("/excluirgenero/<int:id>")
def excluirgenero(id):
    ok, genero = PegaGeneroPorId(id)
    if not ok:
        return render_template('error.html', message=genero)
    
    return render_template('generos/excluirgenero.html', genero=genero)

@app.route("/delete_genero/<int:id>", methods=["POST"])
def delete_genero(id):
    ok, message = DeletarGenero(id)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listargeneros'))

# ---------------- EMPRÉSTIMOS ----------------
@app.route("/listaremprestimos")
def listaremprestimos():
    ok, emprestimos = ListarEmprestimos()
    if not ok:
        return render_template('error.html', message=emprestimos)
    return render_template('emprestimos/listaremprestimos.html', emprestimos=emprestimos)

@app.route("/emprestar", methods=['GET', 'POST'])
def emprestar():
    if request.method == 'POST':
        id_livro = request.form['id_livro']
        id_usuario = request.form['id_usuario']
        ok, message = RealizarEmprestimo(id_livro, id_usuario)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listaremprestimos'))
    
    ok_livros, livros = ListarLivros()
    ok_usuarios, usuarios = ListarUsuarios()
    if not ok_livros or not ok_usuarios:
        return render_template('error.html', message="Erro ao buscar livros ou usuários")
    
    return render_template('emprestimos/emprestar.html', livros=livros, usuarios=usuarios)

@app.route("/devolverlivro/<int:id>", methods=['GET', 'POST'])
def devolverlivro(id):
    if request.method == 'POST':
        ok, message = DevolverLivro(id)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listaremprestimos'))

    ok, emprestimo = PegaEmprestimoPorId(id)
    if not ok:
        return render_template('error.html', message=emprestimo)

    return render_template('emprestimos/devolver.html', emprestimo=emprestimo)

# Adicione esta rota para processar a devolução via POST
@app.route("/devolver_emprestimo/<int:id>", methods=["POST"])
def devolver_emprestimo(id):
    ok, message = DevolverLivro(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listaremprestimos'))

@app.route("/renovar/<int:id>", methods=['GET', 'POST'])
def renovar(id):
    if request.method == 'POST':
        ok, message = RenovarEmprestimo(id)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listaremprestimos'))

    ok, emprestimo = PegaEmprestimoPorId(id)
    if not ok:
        return render_template('error.html', message=emprestimo)
    return render_template('emprestimos/renovar.html', emprestimo=emprestimo)

@app.route("/update_emprestimo/<int:id>", methods=["POST"])
def update_emprestimo(id):
    ok, message = RenovarEmprestimo(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listaremprestimos'))

@app.route("/listaratrasados")
def listaratrasados():
    ok, emprestimos = ListarAtrasados()
    if not ok:
        return render_template('error.html', message=emprestimos)
    return render_template('emprestimos/listaratrasados.html', emprestimos=emprestimos)

# ---------------- MULTAS ----------------
@app.route("/listarmultas")
def listarmultas():
    ok, multas = ListarMultas()
    if not ok:
        return render_template('error.html', message=multas)
    return render_template('multas/listarmultas.html', multas=multas)

@app.route("/removermulta/<int:id>", methods=["GET", "POST"])
def removermulta(id):
    if request.method == 'POST':
        ok, message = RemoverMulta(id)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listarmultas'))

    ok, multa = PegaMultaPorId(id)
    if not ok:
        return render_template('error.html', message=multa)

    return render_template('multas/removermulta.html', multa=multa)

# Rotas API
@app.route("/auth/register", methods=["POST"])
def route_register():
    data = request.json or {}
    nome = data.get("nome_completo")
    email = data.get("email")
    senha = data.get("senha")
    telefone = data.get("telefone")
    tipo = data.get("tipo_usuario", "aluno")

    if not nome or not email or not senha:
        return jsonify({"error": "nome, email e senha são obrigatórios"}), 400

    ok, res = CadastroUser(nome, email, senha, telefone=telefone, tipo_usuario=tipo)
    if not ok:
        return jsonify({"error": res}), 409
    
    return jsonify({"message": "Usuário criado", "id_usuario": res}), 201

@app.route("/auth/login", methods=["POST"])
def route_login():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")

    if not email or not senha:
        return jsonify({"error": "email e senha são obrigatórios"}), 400
    
    ok, res = VerificaLoginUsuario(email, senha)
    if not ok:
        return jsonify({"error": res}), 401
    
    user = res.get("usuario")
    novaHash = res.get("novaHash")
    is_admin = res.get("is_admin", False)

    identity = {
        "id_usuario": user["id_usuario"],
        "email": user["email"],
        "tipo": user.get("tipo_usuario"),
        "is_admin": is_admin
    }

    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    if novaHash:
        try: 
            from userModel import AtualizaHashSenha
            AtualizaHashSenha(user["id_usuario"], novaHash)
        except Exception as e:
            print(f"Aviso: novaHash disponivel mas não foi possivel atualizar no DB: {e}")

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user,
        "is_admin": is_admin
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)