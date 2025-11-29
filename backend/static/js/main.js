const API_BASE = 'http://127.0.0.1:5000';




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
        captchaForm.addEventListener('submit', function (e) {
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

// // Função para verificar se usuário está logado
// function verificarLogin() {
//     const token = localStorage.getItem('bf_access');
//     if (token) {
//         // Se está na página de login e já tem token, redireciona
//         if (window.location.pathname === '/login') {
//             window.location.href = '/';
//         }

//         // Atualiza header para mostrar opção de logout
//         const menu = document.querySelector('.menu');
//         if (menu) {
//             const loginItem = menu.querySelector('a[href="/login"]');
//             if (loginItem) {
//                 loginItem.textContent = 'Sair';
//                 loginItem.href = '#';
//                 loginItem.addEventListener('click', function (e) {
//                     e.preventDefault();
//                     localStorage.removeItem('bf_access');
//                     localStorage.removeItem('bf_refresh');
//                     window.location.href = '/';
//                 });
//             }
//         }
//     }
// }

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
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('search-input');
    const bookCards = document.querySelectorAll('.book-card');

    searchInput.addEventListener('input', function () {
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
    document.getElementById('search-form').addEventListener('submit', function (e) {
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
window.addEventListener('click', function (event) {
    if (event.target === modal) {
        fecharModal();
    }
});

// Processar formulário de empréstimo
document.getElementById('formEmprestimo').addEventListener('submit', async function (e) {
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

//Mostrar senha

document.addEventListener("DOMContentLoaded", function () {
    const senhaInput = document.getElementById("senha");
    const toggleBtn = document.getElementById("toggleSenha");

    if (!senhaInput || !toggleBtn) {
        // elementos não encontrados — não quebra a página
        console.warn("Toggle senha: elemento não encontrado (id 'senha' ou 'toggleSenha').");
        return;
    }

    // ícones SVG (string) — olho e olho risc
    const olho = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>';
    const olhoRisc = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.66 20.66 0 0 1 4.05-5.06"/><path d="M1 1l22 22"/></svg>';

    // inicial: olho (já no HTML), mas vamos garantir
    toggleBtn.innerHTML = olho;

    toggleBtn.addEventListener("click", function () {
        const isPassword = senhaInput.getAttribute("type") === "password";
        senhaInput.setAttribute("type", isPassword ? "text" : "password");
        toggleBtn.innerHTML = isPassword ? olhoRisc : olho;
        toggleBtn.setAttribute("aria-label", isPassword ? "Ocultar senha" : "Mostrar senha");
        // opcional: manter foco no input
        senhaInput.focus();
    });
});

// Menu Mobile
document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', function () {
            mainNav.classList.toggle('active');
        });
    }

    // Fechar menu ao clicar em um link (mobile)
    const navLinks = document.querySelectorAll('.nav-link, .btn-logout');
    navLinks.forEach(link => {
        link.addEventListener('click', function () {
            mainNav.classList.remove('active');
        });
    });
});

// Busca na API Google Books
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const termo = document.getElementById('search-term').value;

    if (termo) {
        fetch(`/api/buscar-livros?q=${encodeURIComponent(termo)}`)
            .then(response => response.json())
            .then(data => {
                const resultsDiv = document.getElementById('api-results');
                if (data.livros && data.livros.length > 0) {
                    resultsDiv.innerHTML = data.livros.map(livro => `
                                <div class="api-livro-card">
                                    <img src="${livro.capa || '/static/img/default-book.png'}" alt="${livro.titulo}">
                                    <div class="api-livro-info">
                                        <h4>${livro.titulo}</h4>
                                        <p><strong>Autor:</strong> ${livro.autores}</p>
                                        <p><strong>Editora:</strong> ${livro.editora}</p>
                                        <p><strong>Ano:</strong> ${livro.ano}</p>
                                        <p class="descricao">${livro.descricao.substring(0, 150)}...</p>
                                        <a href="${livro.link}" target="_blank" class="btn-secondary">Ver mais</a>
                                    </div>
                                </div>
                            `).join('');
                } else {
                    resultsDiv.innerHTML = '<p>Nenhum livro encontrado.</p>';
                }
            })
            .catch(error => {
                console.error('Erro na busca:', error);
                document.getElementById('api-results').innerHTML = '<p>Erro na busca. Tente novamente.</p>';
            });
    }
});

