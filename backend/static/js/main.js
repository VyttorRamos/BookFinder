const API_BASE = 'http://127.0.0.1:5000';

function carregarHeader() {
    const headerContainer = document.createElement('header');

    const path = window.location.pathname;
    const paginaAtual = path.split('/').pop() || 'index.html';

    headerContainer.innerHTML = `
        <nav>
            <div class="logo">
                <a href="/" title="BookFinder">
                    <img src="/static/img/BookFinderIcon.png" alt="Logo BookFinder" />
                </a>
            </div>
            <ul class="menu">
                <li><a href="/" class="${paginaAtual === '' || paginaAtual === '/' || paginaAtual === 'index.html' ? 'active' : ''}">Início</a></li>
                <li><a href="/generos" class="${paginaAtual === 'generos' ? 'active' : ''}">Gêneros</a></li>
                <li><a href="/sobre" class="${paginaAtual === 'sobre' ? 'active' : ''}">Sobre</a></li>
                <li><a href="/contato" class="${paginaAtual === 'contato' ? 'active' : ''}">Contato</a></li>
                <li><a href="/login" class="${paginaAtual === 'login' ? 'active' : ''}">Entre</a></li>
            </ul>
        </nav>
    `;

    document.body.prepend(headerContainer);
}

function carregarFooter() {
    const footerContainer = document.createElement('footer');

    footerContainer.innerHTML = `
        <div class="footer-content">
            <p>&copy; ${new Date().getFullYear()} BookFinder. Todos os direitos reservados.</p>
            <p>Sua biblioteca acadêmica para encontrar as melhores leituras.</p>
            <ul class="footer-links">
                <li><a href="/termos">Termos de Serviço</a></li>
                <li><a href="/privacidade">Política de Privacidade</a></li>
                <li><a href="/contato">Fale Conosco</a></li>
            </ul>
        </div>
    `;

    document.body.appendChild(footerContainer);
}

function configurarBusca() {
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const searchTerm = document.getElementById('search-input').value.trim();
            if (searchTerm) {
                // Redireciona para a página de resultados de busca
                window.location.href = `/busca?q=${encodeURIComponent(searchTerm)}`;
            }
        });
    }
}

// Função para configurar CAPTCHA
function configurarCaptcha() {
    const captchaForm = document.querySelector('form');
    const captchaInput = document.getElementById('notrobo');
    
    if (captchaForm && captchaInput) {
        captchaForm.addEventListener('submit', function(e) {
            if (!captchaInput.value.trim()) {
                e.preventDefault();
                MostrarMensagem('Por favor, responda a pergunta do CAPTCHA.', true);
                captchaInput.focus();
                return false;
            }
            
            // Verificação básica de números (opcional)
            const resposta = captchaInput.value.trim();
            if (!/^\d+$/.test(resposta)) {
                e.preventDefault();
                MostrarMensagem('A resposta deve conter apenas números.', true);
                captchaInput.focus();
                return false;
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    carregarHeader();
    carregarFooter();
    configurarBusca();
    configurarCaptcha();
});

function log(msg) {
    console.log('[BookFinder]', msg);
}

function MostrarMensagem(mensagem, isError = false) {
    // Primeiro tenta encontrar uma mensagem existente
    let el = document.querySelector('.msg');
    
    // Se não existe, cria uma
    if (!el) {
        el = document.createElement('div');
        el.className = 'msg';
        document.querySelector('main').prepend(el);
    }
    
    el.textContent = mensagem;
    el.style.cssText = `
        padding: 12px;
        margin: 15px 0;
        border-radius: 6px;
        font-weight: bold;
        text-align: center;
        background-color: ${isError ? '#f8d7da' : '#d1edff'};
        color: ${isError ? '#721c24' : '#004085'};
        border: 1px solid ${isError ? '#f5c6cb' : '#b8daff'};
    `;
    
    // Remove a mensagem após 5 segundos
    setTimeout(() => {
        if (el && el.parentNode) {
            el.parentNode.removeChild(el);
        }
    }, 5000);
}

async function Registro(e) {
    e.preventDefault();

    const nome = document.getElementById('nome')?.value?.trim();
    const tel = document.getElementById('tel')?.value?.trim();
    const email = document.getElementById('email')?.value?.trim();
    const senha = document.getElementById('senha')?.value;
    const senha_confirm = document.getElementById('senha_confirm')?.value;

    if (!nome || !email || !senha) {
        MostrarMensagem('Preencher nome, email e senha!', true);
        return;
    }
    if (senha !== senha_confirm) {
        MostrarMensagem('As senhas não são iguais.', true);
        return;
    }

    // Validação de email básica
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        MostrarMensagem('Por favor, insira um email válido.', true);
        return;
    }

    try {
        const res = await fetch(API_BASE + '/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome_completo: nome,
                email: email,
                senha: senha,
                telefone: tel
            })
        });

        const json = await res.json();
        if (res.ok) {
            MostrarMensagem('Registrado com sucesso. Faça login para continuar!');
            setTimeout(() => window.location.href = '/login', 2000);
        } else {
            MostrarMensagem(json.error || json.mensagem || 'Erro no registro', true);
        }
    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro de rede ao registrar. Verifique o CORS.', true);
    }
}

async function Login(e) {
    e.preventDefault();
    const email = document.getElementById('email')?.value?.trim();
    const senha = document.getElementById('senha')?.value;

    if (!email || !senha) {
        MostrarMensagem('Preencha email e senha.', true);
        return;
    }

    // Validação de email básica
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        MostrarMensagem('Por favor, insira um email válido.', true);
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
            if (json.access_token) {
                localStorage.setItem('bf_access', json.access_token);
                localStorage.setItem('bf_refresh', json.refresh_token || '');
            }
            localStorage.setItem('bf_last_email', email);

            MostrarMensagem('Login realizado com sucesso.');

            // Verifica se o usuário é admin
            if (json.user && (json.user.tipo_usuario === 'admin' || json.is_admin)) {
                setTimeout(() => window.location.href = '/dashboard', 700);
            } else {
                setTimeout(() => window.location.href = '/', 700);
            }

        } else {
            MostrarMensagem(json.error || json.message || 'Credenciais inválidas', true);
        }

    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro de rede ao logar. Verifique o backend e CORS.', true);
    }
}

// Função para verificar se usuário está logado
function verificarLogin() {
    const token = localStorage.getItem('bf_access');
    if (token) {
        // Não redirecionar automaticamente se usuário já estiver logado.
        // Apenas atualiza o menu para exibir opção de logout quando aplicável.
        const menu = document.querySelector('.menu');
        if (menu) {
            const loginItem = menu.querySelector('a[href="/login"]');
            if (loginItem) {
                loginItem.textContent = 'Sair';
                loginItem.href = '#';
                // Remover listeners duplicados antes de adicionar
                loginItem.replaceWith(loginItem.cloneNode(true));
                const newLoginItem = menu.querySelector('a[href="#"]');
                if (newLoginItem) {
                    newLoginItem.addEventListener('click', function(e) {
                        e.preventDefault();
                        localStorage.removeItem('bf_access');
                        localStorage.removeItem('bf_refresh');
                        window.location.href = '/';
                    });
                }
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // register form
    if (document.getElementById('nome')) {
        const form = document.querySelector('form');
        form.addEventListener('submit', Registro);
        log('Register handler attached');
    }

    // login form
    if (document.getElementById('senha') && document.getElementById('email') && !document.getElementById('nome')) {
        const form = document.querySelector('form');
        form.addEventListener('submit', Login);
        log('Login handler attached');
        const last = localStorage.getItem('bf_last_email');
        if (last) document.getElementById('email').value = last;
    }
    
    verificarLogin();
});

// ===== navegação dos selects do dashboard =====
(function attachAdminSelectNavigation() {
    function init() {
        const selects = document.querySelectorAll('.admin-select');
        selects.forEach(select => {
            select.addEventListener('change', (e) => {
                const url = (e.target && e.target.value) ? e.target.value.trim() : '';
                if (!url) return;
                console.log('[Dashboard] navegando para', url);
                window.location.href = url;
            });
        });
        if (selects.length === 0) console.warn('[Dashboard] nenhum .admin-select encontrado.');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
    // Função de busca em tempo real
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('search-input');
        const bookCards = document.querySelectorAll('.book-card');
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            bookCards.forEach(card => {
                const titulo = card.getAttribute('data-titulo');
                const categoria = card.getAttribute('data-categoria');
                const autor = card.getAttribute('data-autor');
                
                const matches = titulo.includes(searchTerm) || 
                               categoria.includes(searchTerm) || 
                               autor.includes(searchTerm);
                
                if (matches || searchTerm === '') {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
        
        // Configurar o formulário de busca para não recarregar a página
        document.getElementById('search-form').addEventListener('submit', function(e) {
            e.preventDefault();
            // A busca já funciona em tempo real, então não precisa fazer nada extra
        });
    });
    
    // Funções do modal de empréstimo
    const modal = document.getElementById('modalEmprestimo');
    
    function abrirModalEmprestimo(livroId, livroTitulo) {
        document.getElementById('livroId').value = livroId;
        document.getElementById('livroInfo').textContent = `Livro: ${livroTitulo}`;
        modal.style.display = 'block';
    }
    
    function fecharModal() {
        modal.style.display = 'none';
        document.getElementById('formEmprestimo').reset();
    }
    
    // Fechar modal ao clicar no X
    document.querySelector('.close').addEventListener('click', fecharModal);
    
    // Fechar modal ao clicar fora dele
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            fecharModal();
        }
    });
    
    // Processar formulário de empréstimo
    document.getElementById('formEmprestimo').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const livroId = formData.get('livro_id');
        const usuarioId = formData.get('usuario_id');
        
        try {
            const response = await fetch('/emprestar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `id_livro=${livroId}&id_usuario=${usuarioId}`
            });
            
            if (response.ok) {
                alert('✅ Empréstimo realizado com sucesso!');
                fecharModal();
            } else {
                const error = await response.text();
                alert('❌ Erro ao realizar empréstimo: ' + error);
            }
        } catch (error) {
            alert('❌ Erro de rede: ' + error);
        }
    });