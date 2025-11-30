/**
 * main.js - Script principal do BookFinder
 * Atualizado para corrigir conflitos de formulário (Editora/Categoria x Registro)
 */

const API_BASE = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {
    console.log('[BookFinder] App inicializado.');

    initMobileMenu();
    initFlashMessages();
    configurarBusca();
    configurarCaptcha();
    configurarAuthInteligente(); // Nova função mais robusta
    configurarSenhaToggle();
    configurarNavegacaoAdmin();
});

/* ==========================================================================
   FUNÇÕES AUXILIARES
   ========================================================================== */

function log(msg) {
    console.log('[BookFinder]', msg);
}

function MostrarMensagem(mensagem, isError = false) {
    let el = document.querySelector('.msg-box');
    
    if (!el) {
        el = document.createElement('div');
        el.className = 'msg-box';
        const main = document.querySelector('main');
        if (main) main.prepend(el);
    }

    el.textContent = mensagem;
    el.style.cssText = `
        padding: 15px;
        margin: 20px auto;
        max-width: 600px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        background-color: ${isError ? '#fee2e2' : '#dcfce7'};
        color: ${isError ? '#dc2626' : '#16a34a'};
        border: 1px solid ${isError ? '#fecaca' : '#bbf7d0'};
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: opacity 0.3s ease;
    `;

    setTimeout(() => {
        if (el && el.parentNode) {
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 300);
        }
    }, 5000);
}

function initFlashMessages() {
    const alerts = document.querySelectorAll('.alert, .flash-message');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);
    }
}

/* ==========================================================================
   AUTENTICAÇÃO INTELIGENTE
   ========================================================================== */

function configurarAuthInteligente() {
    // Itera sobre TODOS os formulários da página para identificar qual é qual
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Verifica quais campos existem DENTRO deste formulário específico
        const temNome = form.querySelector('input[name="nome_completo"]') || form.querySelector('#nome');
        const temEmail = form.querySelector('input[name="email"]') || form.querySelector('#email');
        const temSenha = form.querySelector('input[name="senha"]') || form.querySelector('#senha');
        const temDescricao = form.querySelector('input[name="descricao"]') || form.querySelector('textarea[name="descricao"]');

        // Lógica de Detecção:
        
        // 1. É Registro de Usuário? (Tem Nome + Email + Senha)
        if (temNome && temEmail && temSenha) {
            // Remove listener padrão para evitar envio tradicional se quisermos AJAX
            // Mas aqui vamos clonar para garantir limpeza
            const novoForm = form.cloneNode(true);
            form.parentNode.replaceChild(novoForm, form);
            novoForm.addEventListener('submit', Registro);
            log('Formulário identificado: Registro de Usuário');
            
            // Reatribuir toggle de senha no novo form
            configurarSenhaToggle();
            return;
        }

        // 2. É Formulário de Categoria ou Editora? (Tem Nome mas NÃO tem Senha)
        if (temNome && !temSenha) {
            // Aqui podemos adicionar validação simples se for Categoria (Nome + Descrição)
            // mas NÃO anexamos a função 'Registro' que pede senha.
            // Deixamos o formulário seguir o fluxo normal do HTML/Flask.
            log('Formulário identificado: Cadastro Geral (Editora/Categoria/Livro) - Fluxo padrão mantido.');
            return;
        }

        // 3. É Login? (Tem Email + Senha, mas NÃO tem Nome)
        if (temEmail && temSenha && !temNome) {
            // Opcional: Se quiser login via AJAX, descomente:
            // form.addEventListener('submit', Login);
            log('Formulário identificado: Login - Fluxo padrão mantido.');
        }
    });
}

async function Registro(e) {
    e.preventDefault();
    const form = e.target; // Pega o formulário que disparou o evento

    // Busca campos DENTRO do formulário disparador
    const nome = form.querySelector('#nome')?.value?.trim() || form.querySelector('input[name="nome_completo"]')?.value?.trim();
    const email = form.querySelector('#email')?.value?.trim() || form.querySelector('input[name="email"]')?.value?.trim();
    const senha = form.querySelector('#senha')?.value;
    const senha_confirm = form.querySelector('#senha_confirm')?.value;
    const tel = form.querySelector('#tel')?.value?.trim() || "";

    if (!nome || !email || !senha) {
        MostrarMensagem('Preencher nome, email e senha!', true);
        return;
    }
    
    // Verifica confirmação apenas se o campo existir
    if (senha_confirm && senha !== senha_confirm) {
        MostrarMensagem('As senhas não são iguais.', true);
        return;
    }

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
        MostrarMensagem('Erro de rede ao registrar.', true);
    }
}

// Login via AJAX (Opcional, mantido para referência)
async function Login(e) {
    e.preventDefault();
    const form = e.target;
    const email = form.querySelector('#email')?.value?.trim();
    const senha = form.querySelector('#senha')?.value;

    if (!email || !senha) {
        MostrarMensagem('Preencha email e senha.', true);
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

            if (json.user && (json.user.tipo_usuario === 'admin' || json.is_admin)) {
                setTimeout(() => window.location.href = '/dashboard', 700);
            } else {
                setTimeout(() => window.location.href = '/home', 700);
            }

        } else {
            MostrarMensagem(json.error || json.message || 'Credenciais inválidas', true);
        }

    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro de rede ao logar.', true);
    }
}

/* ==========================================================================
   BUSCA E FILTROS
   ========================================================================== */

function configurarBusca() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');
    
    if (searchInput) {
        const bookCards = document.querySelectorAll('.book-card');
        
        searchInput.addEventListener('input', function() {
            const term = this.value.toLowerCase().trim();
            
            bookCards.forEach(card => {
                const titulo = card.getAttribute('data-titulo') || '';
                const categoria = card.getAttribute('data-categoria') || '';
                const autor = card.getAttribute('data-autor') || '';
                
                const matches = titulo.includes(term) || categoria.includes(term) || autor.includes(term);
                card.style.display = matches ? 'flex' : 'none';
            });
        });
    }

    if (searchForm && document.querySelector('.book-grid')) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
}

/* ==========================================================================
   CAPTCHA
   ========================================================================== */

function configurarCaptcha() {
    const captchaInput = document.getElementById('notrobo');
    if (!captchaInput) return;

    const form = captchaInput.closest('form');
    if (form) {
        if (form.getAttribute('data-captcha-listener') === 'true') return;
        
        form.addEventListener('submit', function(e) {
            if (!captchaInput.value.trim()) {
                e.preventDefault();
                MostrarMensagem('Por favor, responda a pergunta do CAPTCHA.', true);
                captchaInput.focus();
            }
        });
        form.setAttribute('data-captcha-listener', 'true');
    }
}

/* ==========================================================================
   INTERFACE DE USUÁRIO (UI)
   ========================================================================== */

function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuBtn && mainNav) {
        const newBtn = mobileMenuBtn.cloneNode(true);
        mobileMenuBtn.parentNode.replaceChild(newBtn, mobileMenuBtn);

        newBtn.addEventListener('click', function() {
            if (mainNav.style.display === 'flex') {
                mainNav.style.display = ''; 
                mainNav.classList.remove('active');
            } else {
                mainNav.style.display = 'flex';
                mainNav.style.flexDirection = 'column';
                mainNav.style.position = 'absolute';
                mainNav.style.top = '80px';
                mainNav.style.left = '0';
                mainNav.style.width = '100%';
                mainNav.style.backgroundColor = 'white';
                mainNav.style.padding = '20px';
                mainNav.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                mainNav.classList.add('active');
            }
        });
        
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mainNav.style.display = ''; 
            });
        });
    }
}

function configurarSenhaToggle() {
    const senhaInput = document.getElementById("senha");
    const toggleBtn = document.getElementById("toggleSenha");

    if (!senhaInput || !toggleBtn) return;

    const newToggle = toggleBtn.cloneNode(true);
    toggleBtn.parentNode.replaceChild(newToggle, toggleBtn);

    const olho = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>';
    const olhoRisc = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a20.66 20.66 0 0 1 4.05-5.06"/><path d="M1 1l22 22"/></svg>';

    newToggle.innerHTML = olho;

    newToggle.addEventListener("click", function () {
        const isPassword = senhaInput.getAttribute("type") === "password";
        senhaInput.setAttribute("type", isPassword ? "text" : "password");
        newToggle.innerHTML = isPassword ? olhoRisc : olho;
    });
}

function configurarNavegacaoAdmin() {
    const selects = document.querySelectorAll('.admin-select');
    if (selects.length === 0) return;

    selects.forEach(select => {
        select.addEventListener('change', (e) => {
            const url = e.target.value;
            if (url) window.location.href = url;
        });
    });
}

/* ==========================================================================
   MODAIS
   ========================================================================== */

window.abrirModalEmprestimo = function(livroId, livroTitulo) {
    const modal = document.getElementById('modalEmprestimo');
    const idInput = document.getElementById('livroId');
    const infoText = document.getElementById('livroInfo');

    if (modal && idInput && infoText) {
        idInput.value = livroId;
        infoText.textContent = `Livro: ${livroTitulo}`;
        modal.style.display = 'flex';
    }
};

window.fecharModal = function() {
    const modal = document.getElementById('modalEmprestimo');
    if (modal) {
        modal.style.display = 'none';
        const form = document.getElementById('formEmprestimo');
        if (form) form.reset();
    }
};

window.onclick = function(event) {
    const modal = document.getElementById('modalEmprestimo');
    if (modal && event.target === modal) {
        window.fecharModal();
    }
};

const formEmprestimo = document.getElementById('formEmprestimo');
if (formEmprestimo) {
    formEmprestimo.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const params = new URLSearchParams();
        for (const pair of formData) {
            params.append(pair[0], pair[1]);
        }

        try {
            const response = await fetch('/emprestar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else if (response.ok) {
                alert('✅ Operação realizada com sucesso!');
                window.fecharModal();
                window.location.reload();
            } else {
                const error = await response.text();
                if (error.includes('<!DOCTYPE html>')) {
                    alert('❌ Ocorreu um erro no servidor.');
                } else {
                    alert('❌ Erro: ' + error);
                }
            }
        } catch (error) {
            console.error(error);
            alert('❌ Erro de rede.');
        }
    });
}