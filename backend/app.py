from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from datetime import timedelta
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from userModel import CadastroUser, PegaUserPorEmail, VerificaLoginUsuario

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "muda_essa_chave")
AcessoExpirado = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
RefreshExpirado = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=AcessoExpirado)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=RefreshExpirado)

jwt = JWTManager(app)

CORS(app)

# rotas de HTML
@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/generos", methods=["GET"])
def generos():
    return render_template('generos.html')

@app.route("/sobre", methods=["GET"])
def sobre():
    return render_template('sobre.html')

@app.route("/contato", methods=["GET"])
def contato():
    return render_template('contato.html')

@app.route("/login", methods=["GET"])
def login():
    return render_template('login.html')

@app.route("/register", methods=["GET"])
def register():
    return render_template('register.html')

@app.route("/privacidade", methods=["GET"])
def privacidade():
    return render_template('privacidade.html')

@app.route("/termos", methods=["GET"])
def termos():
    return render_template('termos.html')

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template('dashboard.html')


# ---------------- USUÁRIOS ----------------
@app.route("/listaruser")
def listaruser():
    return render_template('usuarios/listaruser.html')

@app.route("/editaruser")
def editaruser():
    return render_template('usuarios/editaruser.html')

@app.route("/excluiruser")
def excluiruser():
    return render_template('usuarios/excluiruser.html')


# ---------------- LIVROS ----------------
@app.route("/listarlivro", methods=["GET"])
def listarlivro():
    return render_template('livros/listarlivro.html')

@app.route("/cadastrarlivro")
def cadastrarlivro():
    return render_template('livros/cadastrarlivro.html')

@app.route("/editarlivro")
def editarlivro():
    return render_template('livros/editarlivro.html')

@app.route("/excluirlivro")
def excluirlivro():
    return render_template('livros/excluirlivro.html')


    # ---------------- GÊNEROS ----------------
@app.route("/listargeneros")
def listargeneros():
    return render_template('generos/listargeneros.html')

@app.route("/cadastrargeneros")
def cadastrargeneros():
    return render_template('generos/cadastrargeneros.html')

@app.route("/editargeneros")
def editargeneros():
    return render_template('generos/editargeneros.html')

@app.route("/excluirgeneros")
def excluirgeneros():
    return render_template('generos/excluirgeneros.html')


    # ---------------- EMPRESTIMOS ----------------
@app.route("/emprestar")
def emprestar():
    return render_template('emprestimos/emprestar.html')

@app.route("/devolver")
def devolver():
    return render_template('emprestimos/devolver.html')

@app.route("/renovar")
def renovar():
    return render_template('emprestimos/renovar.html')

@app.route("/listaratrasados")
def listaratrasados():
    return render_template('emprestimos/listaratrasados.html')


    # ---------------- MULTAS ----------------
@app.route("/listarmulta")
def listarmulta():
    return render_template('multas/listarmulta.html')

@app.route("/removermulta")
def removermulta():
    return render_template('multas/removermulta.html')

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


@app.route("/books", methods=["GET"])
def get_books():
    books = [
        {"id": 1, "title": "Introdução à Álgebra", "author": "Fulano"},
        {"id": 2, "title": "Cálculo I", "author": "Beltrano"},
    ]
    return jsonify(books)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)