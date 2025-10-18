const APIBase = 'http://localhost:10.108.26.93:5000';

// Função para gerar o cabeçalho (barra de navegação)
function carregarHeader() {
    const headerContainer = document.createElement('header');

    // Identifica qual página está ativa para destacar o link no menu
    const paginaAtual = window.location.pathname.split('/').pop();

    headerContainer.innerHTML = `
        <nav>
            <div class="logo">
                <a href="index.html" title="BookFinder">
                    <img src="img/BookFinderIcon.png" alt="Logo BookFinder" />
                </a>
            </div>
            <ul class="menu">
                <li><a href="index.html#destaques" class="${paginaAtual.includes('index') || paginaAtual === '' ? 'active' : ''}">Recomendações</a></li>
                <li><a href="generos.html" class="${paginaAtual === 'generos.html' ? 'active' : ''}">Gêneros</a></li>
                <li><a href="sobre.html" class="${paginaAtual === 'sobre.html' ? 'active' : ''}">Sobre</a></li>
                <li><a href="contato.html" class="${paginaAtual === 'contato.html' ? 'active' : ''}">Contato</a></li>
                <li><a href="login.html" class="${paginaAtual === 'contato.html' ? 'active' : ''}">Entre</a></li>
            </ul>
        </nav>
    `;

    // Adiciona o cabeçalho ao corpo do documento
    document.body.prepend(headerContainer);
}

// Função para gerar o rodapé
function carregarFooter() {
    const footerContainer = document.createElement('footer');

    footerContainer.innerHTML = `
        <div class="footer-content">
            <p>&copy; ${new Date().getFullYear()} BookFinder. Todos os direitos reservados.</p>
            <p>Sua biblioteca acadêmica para encontrar as melhores leituras.</p>
            <ul class="footer-links">
                <li><a href="termos.html">Termos de Serviço</a></li>
                <li><a href="privacidade.html">Política de Privacidade</a></li>
                <li><a href="contato.html">Fale Conosco</a></li>
            </ul>
        </div>
    `;

    // Adiciona o rodapé ao final do corpo do documento
    document.body.appendChild(footerContainer);
}

// Chama as funções para carregar o cabeçalho e o rodapé quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    carregarHeader();
    carregarFooter();
});

function log(msg) {
    console.log('[BookFinder]', msg);
}

//Função para mostrar mensagem ao usuário
function MostrarMensagem(mensagem, isError = False) {
    const el = document.querySelector('.msg');
    if (el) {
        el.textContent = mensagem;
        el.style.color = isError ? "crimson" : 'green';
    } else {
        alert(mensagem);
    }
}

//Registro
async function Registro(e) {
    e.prevenDefault();

    const nome = document.getElementById('nome')?.value?.trim();
    const tel = document.getElementById('tel')?.value?.trim();
    const email = document.getElementById('email')?.value?.trim();
    const senha = document.getElementById('senha')?.value;
    const senha_confirm = document.getElementById('senha_confirm')?.value;
}

if (!nome || !email || senha) {
    MostrarMensagem('Preencher nome, email e senha!', true);
    return;
}
if (senha !== senha_confirm) {
    MostrarMensagem('As senhas não são iguais.', true);
    return;
}

try {
    const res = await fetch(APIBase + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nome_completo: nome,
            email: email,
            senha: senha,
            telefone: tel
        })
    })

    const json = await res.json();
    if (res.ok) {
        MostrarMensagem('Registrado com sucesso. Faça login para continuar!');
        setTimeout(() => window.location.href = 'login.html', 10000);
    } else {
        MostrarMensagem(json.error || json.mensagem || 'Erro no registro', true);
    }
} catch (err) {
    console.error(err);
    MostrarMensagem('Erro de rede ao registrar. Verifique o CORS.', true);
}

//Login
async function Login(e) {
    e.prevenDefault();
    const email = document.getElementById('email')?.value?.trim();
    const senha = document.getElementById('senha')?.value;
    if (!email || !senha) {
        showMessage('Preencha email e senha.', true);
        return;
    }

    try {
        const res = await fetch(API_BASE + '/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, senha: senha })
        });

        const json = await res.json();
        if (res.ok) {
            //backend retornar tokens:
            if (json.access_token) {
                localStorage.setItem('bf_access', json.access_token);
                localStorage.setItem('bf_refresh', json.refresh_token || '');
            }
            //salva último email
            localStorage.setItem('bf_last_email', email);

            //backend retorna user object
            showMessage('Login realizado com sucesso.');
            // redirecionar para página principal
            setTimeout(() => window.location.href = 'index.html', 700);
        } else {
            showMessage(json.error || json.message || 'Credenciais inválidas', true);
        }
    } catch (err) {
        console.error(err);
        showMessage('Erro de rede ao logar. Verifique o backend e CORS.', true);
    }
}

//vincula os formulários
document.addEventListener('DOMContentLoaded', () => {
    // register form
    const registerForm = document.querySelector('form[action="#"] input#nome') ? document.querySelector('form') : null;
    if (document.getElementById('nome')) {
        const form = document.querySelector('form');
        form.addEventListener('submit', handleRegister);
        log('Register handler attached');
    }

    // login form
    if (document.getElementById('senha') && document.getElementById('email') && !document.getElementById('nome')) {
        const form = document.querySelector('form');
        form.addEventListener('submit', handleLogin);
        log('Login handler attached');
        const last = localStorage.getItem('bf_last_email');
        if (last) document.getElementById('email').value = last;
    }
});