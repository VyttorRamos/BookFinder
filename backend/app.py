from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from datetime import timedelta
from flask import Flask, jsonify, request, abort
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
from copiasModel import (ListarCopias, CadastrarCopia, PegaCopiaPorId, AtualizarCopia, DeletarCopia)


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


@app.route('/api/editoras', methods=['GET', 'POST'])
def api_editoras():
    if request.method == 'GET':
        ok, editoras = ListarEditoras()
        if not ok:
            return jsonify({'error': editoras}), 500
        out = []
        for e in editoras:
            out.append({
                'id': e.get('id_editora'),
                'nome': e.get('nome'),
                'endereco': e.get('endereco') or '',
                'telefone': e.get('telefone') or '',
                'email': e.get('email') or ''
            })
        return jsonify({'editoras': out}), 200

    # POST - criar editora (espera JSON)
    data = request.get_json() or {}
    nome = data.get('nome')
    endereco = data.get('endereco')
    telefone = data.get('telefone')
    email = data.get('email')

    if not nome:
        return jsonify({'error': 'nome é obrigatório'}), 400

    ok, res = CadastrarEditora(nome, endereco, telefone, email)
    if not ok:
        return jsonify({'error': res}), 500

    return jsonify({'message': res}), 201


@app.route('/api/editoras/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_editora_detail(id):
    if request.method == 'GET':
        ok, editora = PegaEditoraPorId(id)
        if not ok:
            return jsonify({'error': editora}), 404
        out = {
            'id': editora.get('id_editora'),
            'nome': editora.get('nome'),
            'endereco': editora.get('endereco') or '',
            'telefone': editora.get('telefone') or '',
            'email': editora.get('email') or ''
        }
        return jsonify(out), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        nome = data.get('nome')
        endereco = data.get('endereco')
        telefone = data.get('telefone')
        email = data.get('email')

        if not nome:
            return jsonify({'error': 'nome é obrigatório'}), 400

        ok, res = AtualizarEditora(id, nome, endereco, telefone, email)
        if not ok:
            return jsonify({'error': res}), 500
        return jsonify({'message': res}), 200

    # DELETE
    ok, res = DeletarEditora(id)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 200


# USUÁRIOS - endpoint API (lista)
@app.route('/api/usuarios', methods=['GET'])
def api_usuarios():
    ok, usuarios = ListarUsuarios()
    if not ok:
        return jsonify({'error': usuarios}), 500
    out = []
    for u in usuarios:
        out.append({
            'id': u.get('id_usuario'),
            'nome_completo': u.get('nome_completo'),
            'email': u.get('email')
        })
    return jsonify({'usuarios': out}), 200


@app.route('/api/usuarios/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_usuario_detail(id):
    if request.method == 'GET':
        ok, usuario = PegaUserPorId(id)
        if not ok:
            return jsonify({'error': usuario}), 404
        return jsonify({'usuario': usuario}), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        nome = data.get('nome_completo')
        email = data.get('email')
        telefone = data.get('telefone')
        tipo_usuario = data.get('tipo_usuario')
        if not nome or not email:
            return jsonify({'error': 'nome_completo e email são obrigatórios'}), 400
        ok, res = AtualizarUsuario(id, nome, email, telefone, tipo_usuario)
        if not ok:
            return jsonify({'error': res}), 500
        return jsonify({'message': res}), 200

    # DELETE
    ok, res = DeletarUsuario(id)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 200


# GÊNEROS - API
@app.route('/api/generos', methods=['GET', 'POST'])
def api_generos():
    if request.method == 'GET':
        ok, generos = ListarGeneros()
        if not ok:
            return jsonify({'error': generos}), 500
        return jsonify({'generos': generos}), 200

    # POST
    data = request.get_json() or {}
    nome = data.get('nome_genero')
    descricao = data.get('descricao')
    if not nome:
        return jsonify({'error': 'nome_genero é obrigatório'}), 400
    ok, res = CadastrarGenero(nome, descricao)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 201


@app.route('/api/generos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_genero_detail(id):
    if request.method == 'GET':
        ok, genero = PegaGeneroPorId(id)
        if not ok:
            return jsonify({'error': genero}), 404
        return jsonify({'genero': genero}), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        nome = data.get('nome_genero')
        descricao = data.get('descricao')
        if not nome:
            return jsonify({'error': 'nome_genero é obrigatório'}), 400
        ok, res = AtualizarGenero(id, nome, descricao)
        if not ok:
            return jsonify({'error': res}), 500
        return jsonify({'message': res}), 200

    ok, res = DeletarGenero(id)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 200


# EMPRÉSTIMOS - listar e criar via API
@app.route('/api/emprestimos', methods=['GET', 'POST'])
def api_emprestimos():
    if request.method == 'GET':
        ok, emprestimos = ListarEmprestimos()
        if not ok:
            return jsonify({'error': emprestimos}), 500
        return jsonify({'emprestimos': emprestimos}), 200

    # POST - criar empréstimo
    data = request.get_json() or {}
    id_livro = data.get('id_livro')
    id_usuario = data.get('id_usuario')
    if not id_livro or not id_usuario:
        return jsonify({'error': 'id_livro e id_usuario são obrigatórios'}), 400

    ok, res = RealizarEmprestimo(id_livro, id_usuario)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 201


# MULTAS - listar e remover via API
@app.route('/api/multas', methods=['GET'])
def api_multas():
    ok, multas = ListarMultas()
    if not ok:
        return jsonify({'error': multas}), 500
    # multas já vem como lista de dicionários do model
    return jsonify({'multas': multas}), 200


@app.route('/api/multas/<int:id>', methods=['DELETE'])
def api_multa_delete(id):
    ok, res = RemoverMulta(id)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 200


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


# COPIAS - listar e criar via API
@app.route('/api/copias', methods=['GET', 'POST'])
def api_copias():
    if request.method == 'GET':
        ok, copias = ListarCopias()
        if not ok:
            return jsonify({'error': copias}), 500
        out = []
        for c in copias:
            out.append({
                'id': c.get('id_copia'),
                'id_livro': c.get('id_livro'),
                'cod_interno': c.get('cod_interno'),
                'status_copia': c.get('status_copia')
            })
        return jsonify({'copias': out}), 200

    # POST - criar copia (espera JSON)
    data = request.get_json() or {}
    id_livro = data.get('id_livro')
    cod_interno = data.get('cod_interno')
    status_copia = data.get('status_copia', 'disponivel')

    if not id_livro:
        return jsonify({'error': 'id_livro é obrigatório'}), 400

    ok, res = CadastrarCopia(id_livro, cod_interno, status_copia)
    if not ok:
        return jsonify({'error': res}), 500
    return jsonify({'message': res}), 201


@app.route('/api/copias/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_copia_detail(id):
    if request.method == 'GET':
        ok, copia = PegaCopiaPorId(id)
        if not ok:
            return jsonify({'error': copia}), 404
        out = {
            'id': copia.get('id_copia'),
            'id_livro': copia.get('id_livro'),
            'cod_interno': copia.get('cod_interno'),
            'status_copia': copia.get('status_copia')
        }
        return jsonify(out), 200

    if request.method == 'PUT':
        data = request.get_json() or {}
        id_livro = data.get('id_livro')
        cod_interno = data.get('cod_interno')
        status_copia = data.get('status_copia')
        ok, res = AtualizarCopia(id, id_livro, cod_interno, status_copia)
        if not ok:
            return jsonify({'error': res}), 500
        return jsonify({'message': res}), 200

    ok, res = DeletarCopia(id)
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

# --- HTML routes removed ---
# This backend now serves only JSON APIs for the React frontend.
# All previous template/form routes were intentionally removed.

@app.route('/')
def home():
    return jsonify({"message": "Backend serves API only. Use the React frontend."}), 200

@app.route('/html-removed')
def html_removed():
    return jsonify({"message": "HTML routes were removed. Use /api/* endpoints."}), 410

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


@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def route_refresh():
    """Refresh access token using a valid refresh token in Authorization header."""
    identity = get_jwt_identity()
    if not identity:
        return jsonify({'error': 'invalid refresh token'}), 401
    new_access = create_access_token(identity=identity)
    return jsonify({'access_token': new_access}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)