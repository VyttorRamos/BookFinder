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

# Rotas de páginas HTML
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

    if novaHash:
        try: 
            from userModel import AtualizaHashSenha
            AtualizaHashSenha(user["id_usuario"], novaHash)
        except Exception as e:
            print(f"Aviso: novaHash disponivel mas não foi possivel atualizar no DB: {e}")

    identity = {"id_usuario": user["id_usuario"], "email": user["email"], "tipo": user.get("tipo_usuario")}
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
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