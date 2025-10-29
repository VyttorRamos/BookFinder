from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from datetime import timedelta
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Importação dos modelos
from userModel import (CadastroUser, PegaUserPorEmail, VerificaLoginUsuario, ListarUsuarios, PegaUserPorId, AtualizarUsuario, DeletarUsuario)
from livroModel import (ListarLivros, CadastrarLivro, PegaLivroPorId, AtualizarLivro, DeletarLivro)
from generoModel import (ListarGeneros, CadastrarGenero, PegaGeneroPorId, AtualizarGenero, DeletarGenero)
from emprestimoModel import (ListarEmprestimos, RealizarEmprestimo, PegaEmprestimoPorId, RenovarEmprestimo, DevolverLivro, ListarAtrasados)
from multaModel import (ListarMultas, PegaMultaPorId, RemoverMulta)

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "muda_essa_chave")
AcessoExpirado = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
RefreshExpirado = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=AcessoExpirado)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=RefreshExpirado)

jwt = JWTManager(app)

CORS(app)

# --- ROTAS HTML ---
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/generos")
def generos():
    return render_template('generos.html')

@app.route("/sobre")
def sobre():
    return render_template('sobre.html')

@app.route("/contato")
def contato():
    return render_template('contato.html')

@app.route("/login")
def login():
    return render_template('login.html')

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

# ---------------- LIVROS ----------------
@app.route("/listarlivros")
def listarlivros():
    ok, livros = ListarLivros()
    if not ok:
        return render_template('error.html', message=livros)
    return render_template('livros/listarlivro.html', livros=livros)

@app.route("/cadastrarlivro", methods=["GET", "POST"])
def cadastrarlivro():
    if request.method == 'POST':
        # Lógica de cadastro
        pass
    return render_template('livros/cadastrarlivro.html')

@app.route("/editarlivro/<int:id>", methods=["GET", "POST"])
def editarlivro(id):
    if request.method == 'POST':
        # Lógica de edição
        pass
    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    return render_template('livros/editarlivro.html', livro=livro)

@app.route("/excluirlivro/<int:id>", methods=["GET", "POST"])
def excluirlivro(id):
    if request.method == 'POST':
        # Lógica de exclusão
        pass
    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    return render_template('livros/excluirlivro.html', livro=livro)

# ---------------- GÊNEROS ----------------
@app.route("/listargeneros")
def listargeneros():
    ok, generos = ListarGeneros()
    if not ok:
        return render_template('error.html', message=generos)
    return render_template('generos/listargeneros.html', generos=generos)

# ... (Rotas para cadastrar, editar, excluir generos) ...

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


# --- ROTAS API ---
@app.route("/auth/register", methods=["POST"])
def route_register():
    data = request.json or {}
    # ... (código existente)

@app.route("/auth/login", methods=["POST"])
def route_login():
    data = request.get_json() or {}
    # ... (código existente)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
