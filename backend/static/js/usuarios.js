// static/js/usuarios.js
const API_BASE = 'http://127.0.0.1:5000';

// Buscar usuário para edição
async function buscarUsuario() {
    const termo = document.getElementById('buscarUsuario').value.trim();
    if (!termo) {
        MostrarMensagem('Digite um ID ou email para buscar', true);
        return;
    }

    try {
        const token = localStorage.getItem('bf_access');
        if (!token) {
            MostrarMensagem('Você precisa estar logado', true);
            return;
        }

        let url;
        // Se for numérico, busca por ID, senão por email
        if (!isNaN(termo)) {
            url = `${API_BASE}/api/usuarios/${termo}`;
        } else {
            // Para buscar por email, precisamos listar todos e filtrar
            const response = await fetch(`${API_BASE}/api/usuarios`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao buscar usuários');
            }
            
            const usuarios = await response.json();
            const usuario = usuarios.find(u => u.email === termo);
            
            if (usuario) {
                preencherFormulario(usuario);
            } else {
                MostrarMensagem('Usuário não encontrado', true);
            }
            return;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Usuário não encontrado');
        }

        const usuario = await response.json();
        preencherFormulario(usuario);

    } catch (err) {
        console.error(err);
        MostrarMensagem(err.message || 'Erro ao buscar usuário', true);
    }
}

function preencherFormulario(usuario) {
    document.getElementById('id_usuario').value = usuario.id_usuario;
    document.getElementById('nome_completo').value = usuario.nome_completo || '';
    document.getElementById('email').value = usuario.email || '';
    document.getElementById('telefone').value = usuario.telefone || '';
    document.getElementById('tipo_usuario').value = usuario.tipo_usuario || 'aluno';
    
    document.getElementById('formEditarUsuario').style.display = 'block';
    document.getElementById('resultadoBusca').innerHTML = `
        <div style="background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px;">
            <strong>Usuário encontrado:</strong> ${usuario.nome_completo} (ID: ${usuario.id_usuario})
        </div>
    `;
}

// Editar usuário
async function editarUsuario(e) {
    e.preventDefault();

    const id = document.getElementById('id_usuario').value;
    const nome = document.getElementById('nome_completo').value.trim();
    const email = document.getElementById('email').value.trim();
    const telefone = document.getElementById('telefone').value.trim();
    const tipo = document.getElementById('tipo_usuario').value;
    const senha = document.getElementById('senha').value;

    if (!nome || !email) {
        MostrarMensagem('Nome e email são obrigatórios', true);
        return;
    }

    try {
        const token = localStorage.getItem('bf_access');
        if (!token) {
            MostrarMensagem('Você precisa estar logado', true);
            return;
        }

        const dados = {
            nome_completo: nome,
            email: email,
            telefone: telefone,
            tipo_usuario: tipo
        };

        if (senha) {
            dados.senha = senha;
        }

        const response = await fetch(`${API_BASE}/api/usuarios/${id}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });

        const resultado = await response.json();

        if (response.ok) {
            MostrarMensagem('Usuário atualizado com sucesso!');
            setTimeout(() => {
                window.location.href = '/listaruser';
            }, 1500);
        } else {
            MostrarMensagem(resultado.error || 'Erro ao atualizar usuário', true);
        }

    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro de rede ao atualizar usuário', true);
    }
}

// Listar todos os usuários (para a página listaruser.html)
async function carregarUsuarios() {
    try {
        const token = localStorage.getItem('bf_access');
        if (!token) {
            MostrarMensagem('Você precisa estar logado', true);
            return;
        }

        const response = await fetch(`${API_BASE}/api/usuarios`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar usuários');
        }

        const usuarios = await response.json();
        exibirUsuarios(usuarios);

    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro ao carregar usuários', true);
    }
}

function exibirUsuarios(usuarios) {
    const container = document.getElementById('listaUsuarios');
    if (!container) return;

    if (usuarios.length === 0) {
        container.innerHTML = '<p>Nenhum usuário cadastrado</p>';
        return;
    }

    const html = usuarios.map(usuario => `
        <div class="usuario-item" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h3>${usuario.nome_completo}</h3>
            <p><strong>ID:</strong> ${usuario.id_usuario}</p>
            <p><strong>Email:</strong> ${usuario.email}</p>
            <p><strong>Telefone:</strong> ${usuario.telefone || 'Não informado'}</p>
            <p><strong>Tipo:</strong> ${usuario.tipo_usuario}</p>
            <p><strong>Status:</strong> ${usuario.status_usuario}</p>
            <div style="margin-top: 10px;">
                <a href="/editaruser" onclick="localStorage.setItem('edit_user_id', ${usuario.id_usuario})" 
                   style="margin-right: 10px; color: #007bff;">Editar</a>
                <button onclick="excluirUsuario(${usuario.id_usuario})" 
                        style="color: #dc3545; border: none; background: none; cursor: pointer;">
                    Excluir
                </button>
            </div>
        </div>
    `).join('');

    container.innerHTML = html;
}

// Excluir usuário
async function excluirUsuario(id) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) {
        return;
    }

    try {
        const token = localStorage.getItem('bf_access');
        if (!token) {
            MostrarMensagem('Você precisa estar logado', true);
            return;
        }

        const response = await fetch(`${API_BASE}/api/usuarios/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const resultado = await response.json();

        if (response.ok) {
            MostrarMensagem('Usuário excluído com sucesso!');
            carregarUsuarios(); // Recarrega a lista
        } else {
            MostrarMensagem(resultado.error || 'Erro ao excluir usuário', true);
        }

    } catch (err) {
        console.error(err);
        MostrarMensagem('Erro de rede ao excluir usuário', true);
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Se estiver na página de listar usuários, carrega a lista
    if (document.getElementById('listaUsuarios')) {
        carregarUsuarios();
    }
    
    // Se estiver na página de editar e há um ID salvo, busca automaticamente
    if (document.getElementById('buscarUsuario')) {
        const savedId = localStorage.getItem('edit_user_id');
        if (savedId) {
            document.getElementById('buscarUsuario').value = savedId;
            buscarUsuario();
            localStorage.removeItem('edit_user_id');
        }
    }
});