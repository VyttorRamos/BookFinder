from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error #tratamento de erros

load_dotenv()  # carrega as variáveis do .env

app = Flask(__name__) #Instancia a aplicação Flask

CORS(app) #acesso ao front

@app.route("/", methods=["GET"]) #registra uma rota HTTP GET no caminho /
def home():
    return jsonify({"message": "API Book"})

@app.route("/books", methods=["GET"])
def get_books():
    books = [
        {"id": 1, "title": "Introdução à Álgebra", "author": "Fulano"},
        {"id": 2, "title": "Cálculo I", "author": "Beltrano"},
    ]
    return jsonify(books)

if __name__ == "__main__": #significa que executa o código apenas se esse arquivo for executado diretamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
