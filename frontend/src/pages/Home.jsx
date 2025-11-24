// pages/Home.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../assets/css/home.css';

const Home = () => {
  const [livros, setLivros] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedLivro, setSelectedLivro] = useState(null);
  const [selectedUsuario, setSelectedUsuario] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const API_BASE_URL = 'http://localhost:5000/api';

  // Função para fazer requests com autenticação
  const fetchWithAuth = async (url, options = {}) => {
    const token = localStorage.getItem('bf_access') || localStorage.getItem('token');
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      }
    };
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, config);
    
    // Se receber 401 (Unauthorized), redireciona para login
    if (response.status === 401) {
      logout();
      navigate('/login');
      throw new Error('Sessão expirada');
    }
    
    return response;
  };

  // Redireciona se não estiver autenticado
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Buscar livros e usuários
  useEffect(() => {
    if (isAuthenticated) {
      carregarDados();
    }
  }, [isAuthenticated]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      setMessage('');
      
      // Buscar livros
      const livrosResponse = await fetchWithAuth(`${API_BASE_URL}/livros`);
      const livrosData = await livrosResponse.json();
      
      // Buscar usuários (apenas se for admin)
      let usuariosData = { success: false, usuarios: [] };
      if (user?.is_admin || user?.tipo_usuario === 'admin') {
        try {
          const usuariosResponse = await fetchWithAuth(`${API_BASE_URL}/usuarios`);
          usuariosData = await usuariosResponse.json();
        } catch (error) {
          console.log('Acesso negado para lista de usuários');
        }
      }

      if (livrosData.success) {
        setLivros(livrosData.livros || []);
      } else {
        setMessage('Erro ao carregar livros: ' + (livrosData.message || 'Erro desconhecido'));
      }

      if (usuariosData.success) {
        setUsuarios(usuariosData.usuarios || []);
      } else {
        setUsuarios([]);
      }

    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      if (error.message !== 'Sessão expirada') {
        setMessage('Erro ao carregar dados do servidor');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/landing');
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) {
      carregarDados();
      return;
    }

    try {
      setLoading(true);
      setMessage('');
      
      const response = await fetchWithAuth(`${API_BASE_URL}/buscar-livros`, {
        method: 'POST',
        body: JSON.stringify({ termo: searchTerm }),
      });

      const data = await response.json();
      
      if (data.success) {
        setLivros(data.livros || []);
        if (data.livros.length === 0) {
          setMessage('Nenhum livro encontrado para sua busca');
        }
      } else {
        setMessage('Erro na busca: ' + (data.message || 'Erro desconhecido'));
      }
    } catch (error) {
      console.error('Erro na busca:', error);
      if (error.message !== 'Sessão expirada') {
        setMessage('Erro ao buscar livros');
      }
    } finally {
      setLoading(false);
    }
  };

  const abrirModalEmprestimo = (livroId) => {
    if (!isAuthenticated) {
      setMessage('⚠️ Você precisa estar logado para realizar empréstimos');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      return;
    }

    const livro = livros.find(l => l.id_livro === livroId);
    
    if (livro && livro.disponivel === false) {
      setMessage('❌ Este livro já está emprestado');
      return;
    }

    setSelectedLivro(livro);
    setSelectedUsuario('');
    setShowModal(true);
    setMessage('');
  };

  const fecharModal = () => {
    setShowModal(false);
    setSelectedLivro(null);
    setSelectedUsuario('');
  };

  const handleEmprestimo = async (e) => {
    e.preventDefault();
    if (!selectedLivro || !selectedUsuario) {
      setMessage('Selecione um usuário para o empréstimo');
      return;
    }

    try {
      setLoading(true);
      setMessage('');
      
      const response = await fetchWithAuth(`${API_BASE_URL}/emprestimos`, {
        method: 'POST',
        body: JSON.stringify({
          livro_id: selectedLivro.id_livro,
          usuario_id: selectedUsuario
        }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage('✅ Empréstimo realizado com sucesso!');
        
        // Atualiza o status do livro localmente
        setLivros(prevLivros => 
          prevLivros.map(livro => 
            livro.id_livro === selectedLivro.id_livro 
              ? { ...livro, disponivel: false } 
              : livro
          )
        );
        
        fecharModal();
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(`❌ Erro: ${data.message || 'Falha no empréstimo'}`);
      }
    } catch (error) {
      console.error('Erro no empréstimo:', error);
      if (error.message !== 'Sessão expirada') {
        setMessage('❌ Erro de conexão com o servidor');
      }
    } finally {
      setLoading(false);
    }
  };

  // Filtrar livros localmente (fallback)
  const filteredLivros = livros.filter(livro => {
    if (!searchTerm) return true;
    
    const term = searchTerm.toLowerCase();
    return (
      livro.titulo.toLowerCase().includes(term) ||
      (livro.autor && livro.autor.toLowerCase().includes(term)) ||
      (livro.categoria_nome && livro.categoria_nome.toLowerCase().includes(term)) ||
      (livro.genero && livro.genero.toLowerCase().includes(term))
    );
  });

  const isAdmin = user?.is_admin || user?.tipo_usuario === 'admin';

  return (
    <div className="book-finder">
      <header className="app-header">
        <div className="header-content">
          <h1>📚 BookFinder</h1>
          <div className="user-info">
            {user ? (
              <>
                <span>Olá, {user.nome_completo}</span>
                {isAdmin && <span className="admin-badge">👑 Admin</span>}
                <button onClick={handleLogout} className="btn-logout">
                  Sair
                </button>
              </>
            ) : (
              <button onClick={() => navigate('/login')} className="btn-login">
                Entrar
              </button>
            )}
          </div>
        </div>
      </header>

      <main>
        <div className="welcome-section">
          <h1>Bem-vindo ao BookFinder, {user?.nome_completo}!</h1>
          <p>
            Encontre seus livros favoritos de forma rápida e fácil. Explore nosso catálogo e 
            descubra novas leituras para todos os gostos.
          </p>
        </div>

        {/* Mensagens do sistema */}
        {message && (
          <div className={`message ${message.includes('✅') ? 'success' : message.includes('❌') ? 'error' : message.includes('⚠️') ? 'warning' : 'info'}`}>
            {message}
          </div>
        )}

        <div className="search-container">
          <form id="search-form" onSubmit={handleSearch}>
            <input 
              type="text" 
              id="search-input" 
              placeholder="Busque por título, autor ou categoria..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              {loading ? '⏳ Buscando...' : '🔍 Buscar'}
            </button>
          </form>
        </div>

        <section id="destaques" className="book-section">
          <h2>📚 {searchTerm ? `Resultados para "${searchTerm}"` : 'Livros em Destaque'}</h2>
          
          {loading ? (
            <div className="loading">
              <p>Carregando livros...</p>
            </div>
          ) : filteredLivros.length > 0 ? (
            <div className="book-grid">
              {filteredLivros.map(livro => (
                <div 
                  key={livro.id_livro}
                  className={`book-card ${livro.disponivel === false ? 'indisponivel' : ''}`}
                >
                  <div className="book-card-image">
                    {livro.capa ? (
                      <img src={livro.capa} alt={`Capa do livro ${livro.titulo}`} />
                    ) : (
                      <div className="book-placeholder">
                        📖
                      </div>
                    )}
                    {livro.disponivel === false && (
                      <div className="book-status">EMPRESTADO</div>
                    )}
                  </div>
                  <div className="book-card-info">
                    <h3>{livro.titulo}</h3>
                    <p className="book-author">
                      {livro.autor ? livro.autor : 'Autor não informado'}
                    </p>
                    <p className="book-year">
                      {livro.ano_publicacao && `Ano: ${livro.ano_publicacao}`}
                    </p>
                    <p className="book-category">
                      {livro.categoria_nome || livro.genero || ''}
                    </p>
                    
                    <button 
                      className={`btn-emprestar ${livro.disponivel === false ? 'disabled' : ''}`}
                      onClick={() => abrirModalEmprestimo(livro.id_livro)}
                      disabled={livro.disponivel === false || loading || !isAdmin}
                      title={!isAdmin ? 'Apenas administradores podem realizar empréstimos' : ''}
                    >
                      {livro.disponivel === false ? '📚 Indisponível' : '📚 Emprestar'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-books">
              <p>📚 {searchTerm ? 'Nenhum livro encontrado para sua busca.' : 'Ainda não há livros cadastrados no sistema.'}</p>
              {isAdmin && (
                <Link to="/livros/cadastrarlivro" className="btn-primary">
                  Cadastrar Primeiro Livro
                </Link>
              )}
            </div>
          )}
        </section>

        {isAdmin && (
          <div className="admin-features">
            <div className="feature-card">
              <h3>🔍 Buscar Livros Online</h3>
              <p>Explore milhares de livros usando a API do Google Books</p>
              <Link to="/buscar_livros" className="btn-primary">Buscar na API</Link>
            </div>

            <div className="feature-card">
              <h3>📊 Dashboard</h3>
              <p>Acesse o painel administrativo para gerenciar o sistema</p>
              <Link to="/dashboard" className="btn-primary">Acessar Dashboard</Link>
            </div>

            <div className="feature-card">
              <h3>👥 Gerenciar Usuários</h3>
              <p>Administre usuários, permissões e empréstimos</p>
              <Link to="/usuarios/listaruser" className="btn-primary">Gerenciar Usuários</Link>
            </div>
          </div>
        )}

        {/* Modal para Empréstimo */}
        {showModal && (
          <div id="modalEmprestimo" className="modal" style={{ display: 'block' }}>
            <div className="modal-content">
              <span className="close" onClick={fecharModal}>&times;</span>
              <h3>📚 Realizar Empréstimo</h3>
              <p id="livroInfo">
                Livro selecionado: <strong>{selectedLivro?.titulo}</strong>
              </p>
              
              <form id="formEmprestimo" onSubmit={handleEmprestimo}>
                <input 
                  type="hidden" 
                  id="livroId" 
                  name="livro_id" 
                  value={selectedLivro?.id_livro || ''} 
                />
                
                <div className="form-group">
                  <label htmlFor="usuarioSelect">Selecione o usuário:</label>
                  <select 
                    id="usuarioSelect" 
                    name="usuario_id" 
                    value={selectedUsuario}
                    onChange={(e) => setSelectedUsuario(e.target.value)}
                    required
                    disabled={loading || usuarios.length === 0}
                  >
                    <option value="">Selecione um usuário...</option>
                    {usuarios.length > 0 ? (
                      usuarios.map(usuario => (
                        <option key={usuario.id_usuario} value={usuario.id_usuario}>
                          {usuario.nome_completo} - {usuario.email}
                        </option>
                      ))
                    ) : (
                      <option value="" disabled>
                        Nenhum usuário disponível
                      </option>
                    )}
                  </select>
                  {usuarios.length === 0 && isAdmin && (
                    <small style={{color: '#666', fontStyle: 'italic'}}>
                      <Link to="/usuarios/listaruser">Cadastrar usuários</Link>
                    </small>
                  )}
                </div>
                
                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="btn-primary"
                    disabled={loading || usuarios.length === 0}
                  >
                    {loading ? '⏳ Processando...' : '✅ Confirmar Empréstimo'}
                  </button>
                  <button 
                    type="button" 
                    className="btn-secondary" 
                    onClick={fecharModal}
                    disabled={loading}
                  >
                    ❌ Cancelar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;