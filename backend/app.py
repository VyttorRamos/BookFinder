from flask_jwt_extended import (JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity)
from datetime import timedelta
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from flask_cors import CORS
import os
from dotenv import load_dotenv
from functools import wraps
import random
import requests
from werkzeug.utils import secure_filename

# Importação dos modelos
from userModel import (CadastroUser, PegaUserPorEmail, VerificaLoginUsuario, ListarUsuarios, PegaUserPorId, AtualizarUsuario, DeletarUsuario, AtualizaHashSenha)
from livroModel import (ListarLivros, CadastrarLivro, PegaLivroPorId, AtualizarLivro, DeletarLivro, VerificarDisponibilidade)
from generoModel import (ListarGeneros, CadastrarGenero, PegaGeneroPorId, AtualizarGenero, DeletarGenero)
from emprestimoModel import (BuscarLivrosDisponiveis, ListarEmprestimos, RealizarEmprestimo, PegaEmprestimoPorId, RenovarEmprestimo, DevolverLivro, ListarAtrasados, ListarEmprestimosPorUsuario)
from multaModel import (ListarMultas, PegaMultaPorId, RemoverMulta, ListarMultasPorUsuario, QuitarMulta)
from editoraModel import (ListarEditoras, CadastrarEditora, PegaEditoraPorId, AtualizarEditora, DeletarEditora)
from configModel import (BuscarConfiguracoes, AtualizarConfiguracoesEmLote, BuscarConfiguracaoPorChave)
from auth.auth_utils import SenhaHash, VerificaSenha

load_dotenv()

app = Flask(__name__)

# Configurações
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "keysecret")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secretkey")
AcessoExpirado = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 900))
RefreshExpirado = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 604800))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=AcessoExpirado)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=RefreshExpirado)

# Configurações para upload de imagens
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Criar diretório de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

jwt = JWTManager(app)

CORS(app)

# --- DECORATOR PARA PROTEGER ROTAS ADMIN ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Acesso não autorizado!', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- DECORATOR PARA VERIFICAR SE USUÁRIO ESTÁ ATIVO ---
def active_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        # Verificar se o usuário ainda está ativo no banco
        user_id = session['user_id']
        ok, usuario = PegaUserPorId(user_id)
        
        if not ok or usuario.get('status_usuario') != 'ativo':
            session.clear()
            flash('Sua conta está inativa. Entre em contato com o administrador.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# --- FUNÇÃO CAPTCHA ---
def gerar_captcha():
    operadores = ['+', '-', '*']
    operador = random.choice(operadores)
    
    if operador == '+':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        resposta = num1 + num2
    elif operador == '-':
        num1 = random.randint(10, 20)
        num2 = random.randint(1, num1 - 1)
        resposta = num1 - num2
    else:  # multiplicação
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 5)
        resposta = num1 * num2
    
    return num1, num2, operador, resposta

# --- API PROXY GOOGLE BOOKS ---
@app.route("/buscar-livros")
@active_user_required
def buscar_livros():
    user_type = session.get('user_type', 'aluno')
    return render_template('buscar_livros.html', user_type=user_type)

@app.route("/api/buscar-livros")
@active_user_required
def api_buscar_livros():
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({"error": "Digite um termo para busca"}), 400
    
    try:
        url = f"https://www.googleapis.com/books/v1/volumes"
        params = {
            'q': termo,
            'maxResults': 12,
            'langRestrict': 'pt'
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

# --- ROTAS PRINCIPAIS ---

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
@active_user_required
def home():
    ok, livros = ListarLivros()
    ok_usuarios, usuarios = ListarUsuarios()
    
    if not ok:
        livros = []
    if not ok_usuarios:
        usuarios = []
    
    user_type = session.get('user_type', 'aluno')
    user_name = session.get('user_name', 'Usuário')
    
    return render_template('home.html', 
                           livros=livros, 
                           usuarios=usuarios,
                           user_type=user_type,
                           user_name=user_name)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        captcha_resposta_usuario = request.form.get("notrobo", "").strip()
        captcha_resposta_correta = request.form.get("captcha_correta", "").strip()
        
        if not captcha_resposta_usuario or captcha_resposta_usuario != captcha_resposta_correta:
            num1, num2, operador, resposta = gerar_captcha()
            return render_template(
                "login.html",
                error="Resposta do CAPTCHA incorreta. Tente novamente.",
                captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
                captcha_correta=resposta,
                email=request.form.get('email', '')
            )

        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        ok, res = VerificaLoginUsuario(email, senha)
        
        if not ok:
            num1, num2, operador, resposta = gerar_captcha()
            return render_template(
                "login.html",
                error=res,
                captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
                captcha_correta=resposta,
                email=email
            )

        usuario = PegaUserPorEmail(email)
        
        # MODIFICADO: Verificação adicional de segurança
        if not usuario or usuario.get('status_usuario') != 'ativo':
            num1, num2, operador, resposta = gerar_captcha()
            return render_template(
                "login.html",
                error="Conta inativa. Entre em contato com o administrador.",
                captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
                captcha_correta=resposta,
                email=email
            )
        
        session['user_id'] = usuario["id_usuario"]
        session['user_type'] = usuario["tipo_usuario"]
        session['user_name'] = usuario["nome_completo"]
        session['user_email'] = usuario["email"]

        if usuario["tipo_usuario"].lower() == "admin":
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("home"))

    num1, num2, operador, resposta = gerar_captcha()
    
    return render_template(
        "login.html",
        captcha_pergunta=f"Quanto é {num1} {operador} {num2}?",
        captcha_correta=resposta
    )

# --- PERFIL DO USUÁRIO ---
@app.route("/perfil")
@active_user_required
def perfil():
    user_id = session['user_id']
    ok, usuario = PegaUserPorId(user_id)
    
    if not ok:
        flash('Erro ao carregar perfil', 'error')
        return redirect(url_for('home'))
    
    # Buscar empréstimos ativos do usuário
    ok_emprestimos, emprestimos_ativos = ListarEmprestimosPorUsuario(user_id)
    
    # Buscar multas pendentes do usuário
    ok_multas, multas_pendentes = ListarMultasPorUsuario(user_id)
    
    return render_template('perfil.html',
                         user_type=session.get('user_type'),
                         user_name=session.get('user_name'),
                         user_email=session.get('user_email'),
                         usuario=usuario,
                         emprestimos_ativos=emprestimos_ativos if ok_emprestimos else [],
                         multas_pendentes=multas_pendentes if ok_multas else [])

@app.route("/atualizar-perfil", methods=["POST"])
@active_user_required
def atualizar_perfil():
    user_id = session['user_id']
    nome_completo = request.form['nome_completo']
    email = request.form['email']
    telefone = request.form.get('telefone', '')
    senha_atual = request.form.get('senha_atual', '')
    nova_senha = request.form.get('nova_senha', '')
    
    # Atualizar informações básicas
    ok, message = AtualizarUsuario(user_id, nome_completo, email, telefone, session.get('user_type'))
    
    if not ok:
        flash('Erro ao atualizar perfil: ' + message, 'error')
        return redirect(url_for('perfil'))
    
    # Atualizar senha se fornecida
    if senha_atual and nova_senha:
        # Verificar senha atual
        usuario = PegaUserPorEmail(email)
        if usuario and VerificaSenha(usuario['senha'], senha_atual):
            # Atualizar senha
            nova_hash = SenhaHash(nova_senha)
            AtualizaHashSenha(user_id, nova_hash)
            flash('Senha atualizada com sucesso!', 'success')
        else:
            flash('Senha atual incorreta!', 'error')
    
    # Atualizar sessão
    session['user_name'] = nome_completo
    session['user_email'] = email
    
    flash('Perfil atualizado com sucesso!', 'success')
    return redirect(url_for('perfil'))

@app.route("/generos")
@active_user_required
def generos():
    ok, generos_lista = ListarGeneros()
    if not ok:
        generos_lista = []
    
    user_type = session.get('user_type', 'aluno')
    return render_template('generos.html', generos=generos_lista, user_type=user_type)

@app.route("/genero/<int:id_genero>")
@active_user_required
def livros_por_genero(id_genero):
    ok, todos_livros = ListarLivros()
    if not ok:
        livros_filtrados = []
    else:
        livros_filtrados = [livro for livro in todos_livros if livro.get('id_categoria') == id_genero]
    
    ok_genero, genero = PegaGeneroPorId(id_genero)
    if not ok_genero:
        genero = {'nome': 'Gênero Desconhecido'}
    
    user_type = session.get('user_type', 'aluno')
    return render_template('livros_por_genero.html', 
                          livros=livros_filtrados, 
                          genero=genero, 
                          user_type=user_type)

@app.route("/sobre")
@active_user_required
def sobre():
    user_type = session.get('user_type', 'aluno')
    return render_template('sobre.html', user_type=user_type)

@app.route("/contato")
@active_user_required
def contato():
    user_type = session.get('user_type', 'aluno')
    return render_template('contato.html', user_type=user_type)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/privacidade")
@active_user_required
def privacidade():
    user_type = session.get('user_type', 'aluno')
    return render_template('privacidade.html', user_type=user_type)

@app.route("/termos")
@active_user_required
def termos():
    user_type = session.get('user_type', 'aluno')
    return render_template('termos.html', user_type=user_type)

@app.route("/dashboard")
@active_user_required
@admin_required
def dashboard():
    user_type = session.get('user_type')
    user_name = session.get('user_name')
    return render_template('dashboard.html', user_type=user_type, user_name=user_name)

# ---------------- CONFIGURAÇÕES ----------------
@app.route("/configuracoes", methods=['GET', 'POST'])
@active_user_required
@admin_required
def configuracoes():
    if request.method == 'POST':
        # Coletar todas as configurações do formulário
        configuracoes_dict = {}
        
        # Configurações de empréstimos
        configuracoes_dict['limite_emprestimos'] = request.form.get('limite_emprestimos')
        configuracoes_dict['prazo_aluno'] = request.form.get('prazo_aluno')
        configuracoes_dict['prazo_professor'] = request.form.get('prazo_professor')
        configuracoes_dict['limite_renovacoes'] = request.form.get('limite_renovacoes')
        configuracoes_dict['dias_renovacao'] = request.form.get('dias_renovacao')
        
        # Configurações de multas
        configuracoes_dict['multa_por_dia'] = request.form.get('multa_por_dia')
        
        # Validar dados
        try:
            # Converter para os tipos corretos
            limite_emprestimos = int(configuracoes_dict['limite_emprestimos'])
            prazo_aluno = int(configuracoes_dict['prazo_aluno'])
            prazo_professor = int(configuracoes_dict['prazo_professor'])
            limite_renovacoes = int(configuracoes_dict['limite_renovacoes'])
            dias_renovacao = int(configuracoes_dict['dias_renovacao'])
            multa_por_dia = float(configuracoes_dict['multa_por_dia'])
            
            # Validações básicas
            if limite_emprestimos < 1 or limite_emprestimos > 10:
                flash('Limite de empréstimos deve estar entre 1 e 10', 'error')
                return redirect(url_for('configuracoes'))
                
            if prazo_aluno < 1 or prazo_aluno > 60:
                flash('Prazo para alunos deve estar entre 1 e 60 dias', 'error')
                return redirect(url_for('configuracoes'))
                
            if prazo_professor < 1 or prazo_professor > 90:
                flash('Prazo para professores deve estar entre 1 e 90 dias', 'error')
                return redirect(url_for('configuracoes'))
                
            if limite_renovacoes < 0 or limite_renovacoes > 5:
                flash('Limite de renovações deve estar entre 0 e 5', 'error')
                return redirect(url_for('configuracoes'))
                
            if dias_renovacao < 1 or dias_renovacao > 30:
                flash('Dias por renovação deve estar entre 1 e 30', 'error')
                return redirect(url_for('configuracoes'))
                
            if multa_por_dia < 0.50 or multa_por_dia > 10.00:
                flash('Multa por dia deve estar entre R$ 0,50 e R$ 10,00', 'error')
                return redirect(url_for('configuracoes'))
                
        except ValueError:
            flash('Por favor, insira valores válidos', 'error')
            return redirect(url_for('configuracoes'))
        
        # Atualizar configurações
        ok, message = AtualizarConfiguracoesEmLote(configuracoes_dict)
        
        if not ok:
            flash(f'Erro ao salvar configurações: {message}', 'error')
        else:
            flash('Configurações atualizadas com sucesso!', 'success')
        
        return redirect(url_for('configuracoes'))
    
    # Buscar configurações atuais
    ok, configuracoes = BuscarConfiguracoes()
    if not ok:
        flash('Erro ao carregar configurações', 'error')
        configuracoes = {}
    
    user_type = session.get('user_type')
    return render_template('configuracoes.html', configuracoes=configuracoes, user_type=user_type)

# ---------------- USUÁRIOS ----------------
@app.route("/listaruser")
@active_user_required
@admin_required
def listaruser():
    ok, usuarios = ListarUsuarios()
    if not ok:
        return render_template('error.html', message=usuarios)
    user_type = session.get('user_type')
    return render_template('usuarios/listaruser.html', usuarios=usuarios, user_type=user_type)

@app.route("/editaruser/<int:id>")
@active_user_required
@admin_required
def editaruser(id):
    ok, usuario = PegaUserPorId(id)
    if not ok:
        return render_template('error.html', message=usuario)
    user_type = session.get('user_type')
    return render_template('usuarios/editaruser.html', usuario=usuario, user_type=user_type)

@app.route("/update_user/<int:id>", methods=["POST"])
@active_user_required
@admin_required
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
@active_user_required
@admin_required
def excluiruser(id):
    ok, usuario = PegaUserPorId(id)
    if not ok:
        return render_template('error.html', message=usuario)
    user_type = session.get('user_type')
    return render_template('usuarios/excluiruser.html', usuario=usuario, user_type=user_type)

@app.route("/delete_user/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def delete_user(id):
    ok, message = DeletarUsuario(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listaruser'))

# ---------------- EDITORAS ----------------
@app.route("/listareditoras")
@active_user_required
@admin_required
def listareditoras():
    ok, editoras = ListarEditoras()
    if not ok:
        return render_template('error.html', message=editoras)
    user_type = session.get('user_type')
    return render_template('editoras/listareditoras.html', editoras=editoras, user_type=user_type)

@app.route("/cadastrareditora", methods=["GET", "POST"])
@active_user_required
@admin_required
def cadastrareditora():
    if request.method == "POST":
        nome = request.form['nome'].strip()
        endereco = request.form.get('endereco', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        
        if not nome:
            user_type = session.get('user_type')
            return render_template('editoras/cadastrareditora.html', 
                                   error="Nome da editora é obrigatório",
                                   user_type=user_type)
        
        ok, message = CadastrarEditora(nome, endereco, telefone, email)
        if not ok:
            user_type = session.get('user_type')
            return render_template('editoras/cadastrareditora.html', 
                                   error=message, nome=nome, endereco=endereco, 
                                   telefone=telefone, email=email,
                                   user_type=user_type)
        
        return redirect(url_for('listareditoras'))
    
    user_type = session.get('user_type')
    return render_template('editoras/cadastrareditora.html', user_type=user_type)

@app.route("/editareditora/<int:id>", methods=["GET", "POST"])
@active_user_required
@admin_required
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
            user_type = session.get('user_type')
            return render_template('editoras/editareditora.html', 
                                   editora=editora, error="Nome da editora é obrigatório",
                                   user_type=user_type)
        
        ok, message = AtualizarEditora(id, nome, endereco, telefone, email)
        if not ok:
            ok, editora = PegaEditoraPorId(id)
            if not ok:
                return render_template('error.html', message=editora)
            user_type = session.get('user_type')
            return render_template('editoras/editareditora.html', 
                                   editora=editora, error=message,
                                   user_type=user_type)
        
        return redirect(url_for('listareditoras'))
    
    ok, editora = PegaEditoraPorId(id)
    if not ok:
        return render_template('error.html', message=editora)
    
    user_type = session.get('user_type')
    return render_template('editoras/editareditora.html', editora=editora, user_type=user_type)

@app.route("/update_editora/<int:id>", methods=["POST"])
@active_user_required
@admin_required
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
@active_user_required
@admin_required
def excluireditora(id):
    ok, editora = PegaEditoraPorId(id)
    if not ok:
        return render_template('error.html', message=editora)
    
    user_type = session.get('user_type')
    return render_template('editoras/excluireditora.html', editora=editora, user_type=user_type)

@app.route("/delete_editora/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def delete_editora(id):
    ok, message = DeletarEditora(id)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listareditoras'))

# ---------------- LIVROS ----------------
@app.route("/listarlivro")
@active_user_required
@admin_required
def listarlivros():
    ok, livros = ListarLivros()
    if not ok:
        return render_template('error.html', message=livros)
    user_type = session.get('user_type')
    return render_template('livros/listarlivro.html', livros=livros, user_type=user_type)

@app.route("/cadastrarlivro", methods=["GET", "POST"])
@active_user_required
@admin_required
def cadastrarlivro():
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        isbn = request.form.get('isbn', '').strip()
        ano_publicacao = request.form.get('ano_publicacao', '').strip()
        id_editora = request.form.get('id_editora')
        id_categoria = request.form.get('id_categoria')
        quantidade_total = request.form.get('quantidade_total', 1)
        
        # Processar upload da capa
        capa = None
        if 'capa' in request.files:
            file = request.files['capa']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    capa = filename
        
        if not titulo:
            return render_template_with_editoras_categorias(
                'livros/cadastrarlivro.html', 
                error="Título do livro é obrigatório"
            )
        
        ok, message = CadastrarLivro(titulo, isbn, ano_publicacao, id_editora, id_categoria, capa, int(quantidade_total))
        if not ok:
            return render_template_with_editoras_categorias(
                'livros/cadastrarlivro.html', 
                error=message, 
                titulo=titulo, 
                isbn=isbn, 
                ano_publicacao=ano_publicacao,
                quantidade_total=quantidade_total
            )
        
        flash('Livro cadastrado com sucesso!', 'success')
        return redirect(url_for('listarlivros'))
    
    return render_template_with_editoras_categorias('livros/cadastrarlivro.html')

@app.route("/editarlivro/<int:id>", methods=["GET", "POST"])
@active_user_required
@admin_required
def editarlivro(id):
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        isbn = request.form.get('isbn', '').strip()
        ano_publicacao = request.form.get('ano_publicacao', '').strip()
        id_editora = request.form.get('id_editora')
        id_categoria = request.form.get('id_categoria')
        quantidade_total = request.form.get('quantidade_total')
        
        # Converter para tipos apropriados
        if ano_publicacao:
            try:
                ano_publicacao = int(ano_publicacao)
            except ValueError:
                ano_publicacao = None
        
        if id_editora:
            try:
                id_editora = int(id_editora)
            except ValueError:
                id_editora = None
        
        if id_categoria:
            try:
                id_categoria = int(id_categoria)
            except ValueError:
                id_categoria = None
        
        if quantidade_total:
            try:
                quantidade_total = int(quantidade_total)
            except ValueError:
                quantidade_total = None
        
        # Processar upload da capa - IMPORTANTE: capa será None se não for enviado novo arquivo
        capa = None
        if 'capa' in request.files:
            file = request.files['capa']
            if file and file.filename != '' and file.filename != 'undefined':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    capa = filename
                else:
                    ok, livro = PegaLivroPorId(id)
                    if not ok:
                        return render_template('error.html', message=livro)
                    return render_template_with_editoras_categorias(
                        'livros/editarlivro.html', 
                        livro=livro, 
                        error="Tipo de arquivo não permitido. Use apenas PNG, JPG, JPEG ou GIF.",
                        user_type=session.get('user_type')
                    )
        
        if not titulo:
            ok, livro = PegaLivroPorId(id)
            if not ok:
                return render_template('error.html', message=livro)
            return render_template_with_editoras_categorias(
                'livros/editarlivro.html', 
                livro=livro, 
                error="Título do livro é obrigatório",
                user_type=session.get('user_type')
            )
        
        ok, message = AtualizarLivro(id, titulo, isbn, ano_publicacao, id_editora, id_categoria, capa, quantidade_total)
        if not ok:
            ok, livro = PegaLivroPorId(id)
            if not ok:
                return render_template('error.html', message=livro)
            return render_template_with_editoras_categorias(
                'livros/editarlivro.html', 
                livro=livro, 
                error=message,
                user_type=session.get('user_type')
            )
        
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('listarlivros'))
    
    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    
    return render_template_with_editoras_categorias(
        'livros/editarlivro.html', 
        livro=livro, 
        user_type=session.get('user_type')
    )

@app.route("/update_livro/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def update_livro(id):
    titulo = request.form['titulo'].strip()
    isbn = request.form.get('isbn', '').strip()
    ano_publicacao = request.form.get('ano_publicacao', '').strip()
    id_editora = request.form.get('id_editora')
    id_categoria = request.form.get('id_categoria')
    
    # Converter para tipos apropriados
    if ano_publicacao:
        try:
            ano_publicacao = int(ano_publicacao)
        except ValueError:
            ano_publicacao = None
    
    if id_editora:
        try:
            id_editora = int(id_editora)
        except ValueError:
            id_editora = None
    
    if id_categoria:
        try:
            id_categoria = int(id_categoria)
        except ValueError:
            id_categoria = None
    
    # Processar upload da capa
    capa = None
    if 'capa' in request.files:
        file = request.files['capa']
        if file and file.filename != '' and file.filename != 'undefined':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                capa = filename
    
    if not titulo:
        return render_template('error.html', message="Título do livro é obrigatório")
    
    ok, message = AtualizarLivro(id, titulo, isbn, ano_publicacao, id_editora, id_categoria, capa)
    if not ok:
        return render_template('error.html', message=message)
    
    flash('Livro atualizado com sucesso!', 'success')
    return redirect(url_for('listarlivros'))

@app.route("/excluirlivro/<int:id>", methods=["GET", "POST"])
@active_user_required
@admin_required
def excluirlivro(id):
    if request.method == 'POST':
        ok, message = DeletarLivro(id)
        if not ok:
            return render_template('error.html', message=message)
        return redirect(url_for('listarlivros'))

    ok, livro = PegaLivroPorId(id)
    if not ok:
        return render_template('error.html', message=livro)
    
    user_type = session.get('user_type')
    return render_template('livros/excluirlivro.html', livro=livro, user_type=user_type)

@app.route("/delete_livro/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def delete_livro(id):
    ok, message = DeletarLivro(id)
    if not ok:
        return render_template('error.html', message=message)
    return redirect(url_for('listarlivros'))

# ---------------- GÊNEROS ----------------
@app.route("/listargeneros")
@active_user_required
@admin_required
def listargeneros():
    ok, generos = ListarGeneros()
    if not ok:
        return render_template('error.html', message=generos)
    user_type = session.get('user_type')
    return render_template('generos/listargeneros.html', generos=generos, user_type=user_type)

@app.route("/cadastrargenero", methods=["GET", "POST"])
@active_user_required
@admin_required
def cadastrargenero():
    if request.method == "POST":
        nome_genero = request.form['nome_genero'].strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome_genero:
            user_type = session.get('user_type')
            return render_template('generos/cadastrargenero.html', 
                                   error="Nome da categoria é obrigatório",
                                   user_type=user_type)
        
        ok, message = CadastrarGenero(nome_genero, descricao)
        if not ok:
            user_type = session.get('user_type')
            return render_template('generos/cadastrargenero.html', 
                                   error=message, nome_genero=nome_genero, descricao=descricao,
                                   user_type=user_type)
        
        return redirect(url_for('listargeneros'))
    
    user_type = session.get('user_type')
    return render_template('generos/cadastrargenero.html', user_type=user_type)

@app.route("/editargenero/<int:id>", methods=["GET", "POST"])
@active_user_required
@admin_required
def editargenero(id):
    if request.method == "POST":
        nome_genero = request.form['nome_genero'].strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome_genero:
            ok, genero = PegaGeneroPorId(id)
            if not ok:
                return render_template('error.html', message=genero)
            user_type = session.get('user_type')
            return render_template('generos/editargenero.html', 
                                   genero=genero, error="Nome da categoria é obrigatório",
                                   user_type=user_type)
        
        ok, message = AtualizarGenero(id, nome_genero, descricao)
        if not ok:
            ok, genero = PegaGeneroPorId(id)
            if not ok:
                return render_template('error.html', message=genero)
            user_type = session.get('user_type')
            return render_template('generos/editargenero.html', 
                                   genero=genero, error=message,
                                   user_type=user_type)
        
        return redirect(url_for('listargeneros'))
    
    ok, genero = PegaGeneroPorId(id)
    if not ok:
        return render_template('error.html', message=genero)
    
    user_type = session.get('user_type')
    return render_template('generos/editargenero.html', genero=genero, user_type=user_type)

@app.route("/update_genero/<int:id>", methods=["POST"])
@active_user_required
@admin_required
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
@active_user_required
@admin_required
def excluirgenero(id):
    ok, genero = PegaGeneroPorId(id)
    if not ok:
        return render_template('error.html', message=genero)
    
    user_type = session.get('user_type')
    return render_template('generos/excluirgenero.html', genero=genero, user_type=user_type)

@app.route("/delete_genero/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def delete_genero(id):
    ok, message = DeletarGenero(id)
    if not ok:
        return render_template('error.html', message=message)
    
    return redirect(url_for('listargeneros'))

# ---------------- EMPRÉSTIMOS ----------------
@app.route("/listaremprestimos")
@active_user_required
@admin_required
def listaremprestimos():
    ok, emprestimos = ListarEmprestimos()
    if not ok:
        flash('Erro ao carregar empréstimos', 'error')
        emprestimos = []
    
    user_type = session.get('user_type')
    return render_template('emprestimos/listaremprestimos.html', emprestimos=emprestimos, user_type=user_type)

@app.route("/emprestar", methods=['GET', 'POST'])
@active_user_required
@admin_required
def emprestar():
    if request.method == 'POST':
        id_livro = request.form['id_livro']
        id_usuario = request.form['id_usuario']
        
        ok, message = RealizarEmprestimo(id_livro, id_usuario)
        if not ok:
            flash(f'Erro: {message}', 'error')
            return redirect(url_for('emprestar'))
        
        flash('Empréstimo realizado com sucesso!', 'success')
        return redirect(url_for('listaremprestimos'))
    
    # Buscar livros disponíveis
    ok_livros, livros = BuscarLivrosDisponiveis()  # Usando a nova função
    if not ok_livros:
        livros_disponiveis = []
    else:
        livros_disponiveis = livros
    
    ok_usuarios, usuarios = ListarUsuarios()
    if not ok_usuarios:
        usuarios = []
    
    user_type = session.get('user_type')
    return render_template('emprestimos/emprestar.html', 
                         livros=livros_disponiveis, 
                         usuarios=usuarios, 
                         user_type=user_type)

@app.route("/api/buscar-livros-disponiveis")
@active_user_required
@admin_required
def api_buscar_livros_disponiveis():
    termo = request.args.get('q', '')
    
    if termo:
        ok, livros = BuscarLivrosDisponiveis(termo)
    else:
        ok, livros = BuscarLivrosDisponiveis()
    
    if not ok:
        return jsonify({"error": livros}), 500
    
    return jsonify({"livros": livros})

@app.route("/devolverlivro/<int:id>", methods=['GET', 'POST'])
@active_user_required
@admin_required
def devolverlivro(id):
    if request.method == 'POST':
        ok, message = DevolverLivro(id)
        if not ok:
            flash(f'Erro: {message}', 'error')
        else:
            flash('Livro devolvido com sucesso!', 'success')
        return redirect(url_for('listaremprestimos'))

    ok, emprestimo = PegaEmprestimoPorId(id)
    if not ok:
        flash('Empréstimo não encontrado', 'error')
        return redirect(url_for('listaremprestimos'))

    user_type = session.get('user_type')
    return render_template('emprestimos/devolver.html', emprestimo=emprestimo, user_type=user_type)

@app.route("/devolver_emprestimo/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def devolver_emprestimo(id):
    ok, message = DevolverLivro(id)
    if not ok:
        flash(f'Erro: {message}', 'error')
    else:
        flash('Livro devolvido com sucesso!', 'success')
    return redirect(url_for('listaremprestimos'))

@app.route("/renovar/<int:id>", methods=['GET', 'POST'])
@active_user_required
@admin_required
def renovar(id):
    if request.method == 'POST':
        ok, message = RenovarEmprestimo(id)
        if not ok:
            flash(f'Erro: {message}', 'error')
        else:
            flash('Empréstimo renovado com sucesso!', 'success')
        return redirect(url_for('listaremprestimos'))

    ok, emprestimo = PegaEmprestimoPorId(id)
    if not ok:
        flash('Empréstimo não encontrado', 'error')
        return redirect(url_for('listaremprestimos'))
    
    user_type = session.get('user_type')
    return render_template('emprestimos/renovar.html', emprestimo=emprestimo, user_type=user_type)

@app.route("/update_emprestimo/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def update_emprestimo(id):
    ok, message = RenovarEmprestimo(id)
    if not ok:
        flash(f'Erro: {message}', 'error')
    else:
        flash('Empréstimo renovado com sucesso!', 'success')
    return redirect(url_for('listaremprestimos'))

@app.route("/listaratrasados")
@active_user_required
@admin_required
def listaratrasados():
    ok, emprestimos = ListarAtrasados()
    if not ok:
        flash('Erro ao carregar empréstimos atrasados', 'error')
        emprestimos = []
    
    user_type = session.get('user_type')
    return render_template('emprestimos/listaratrasados.html', emprestimos=emprestimos, user_type=user_type)

# ---------------- MULTAS ----------------
@app.route("/listarmultas")
@active_user_required
@admin_required
def listarmultas():
    ok, multas = ListarMultas()
    if not ok:
        flash('Erro ao carregar multas', 'error')
        multas = []
    
    user_type = session.get('user_type')
    return render_template('multas/listarmultas.html', multas=multas, user_type=user_type)

@app.route("/removermulta/<int:id>", methods=["GET", "POST"])
@active_user_required
@admin_required
def removermulta(id):
    if request.method == 'POST':
        ok, message = RemoverMulta(id)
        if not ok:
            flash(f'Erro: {message}', 'error')
        else:
            flash('Multa removida com sucesso!', 'success')
        return redirect(url_for('listarmultas'))

    ok, multa = PegaMultaPorId(id)
    if not ok:
        flash('Multa não encontrada', 'error')
        return redirect(url_for('listarmultas'))

    user_type = session.get('user_type')
    return render_template('multas/removermulta.html', multa=multa, user_type=user_type)

@app.route("/quitarmulta/<int:id>", methods=["POST"])
@active_user_required
@admin_required
def quitarmulta(id):
    ok, message = QuitarMulta(id)
    if not ok:
        flash(f'Erro: {message}', 'error')
    else:
        flash('Multa quitada com sucesso!', 'success')
    return redirect(url_for('listarmultas'))

# ---------------- FUNÇÕES AUXILIARES ----------------
def render_template_with_editoras_categorias(template, **kwargs):
    """Função auxiliar para carregar editoras e categorias nos templates"""
    ok_editoras, editoras = ListarEditoras()
    ok_categorias, categorias = ListarGeneros()
    
    if not ok_editoras:
        editoras = []
    if not ok_categorias:
        categorias = []
    
    return render_template(template, 
                          editoras=editoras, 
                          categorias=categorias, 
                          **kwargs)

# ---------------- API AUTH ----------------
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