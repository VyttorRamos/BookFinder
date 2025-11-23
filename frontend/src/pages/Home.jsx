import React, { useState, useEffect } from 'react';
import '../assets/css/home.css';

const BookFinder = () => {
  const [livros, setLivros] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [selectedLivro, setSelectedLivro] = useState(null);
  const [selectedUsuario, setSelectedUsuario] = useState('');

  // Simulando dados iniciais - você precisará substituir por chamadas de API reais
  useEffect(() => {
    // Aqui você faria a chamada para sua API
    // fetch('/api/livros').then(response => response.json()).then(data => setLivros(data));
    // fetch('/api/usuarios').then(response => response.json()).then(data => setUsuarios(data));
    
    // Dados mock para exemplo
    const mockLivros = [
      {
        id_livro: 1,
        titulo: "Dom Casmurro",
        autor: "Machado de Assis",
        ano_publicacao: 1899,
        categoria_nome: "Literatura Brasileira",
        capa: "/covers/dom-casmurro.jpg"
      },
      // ... mais livros
    ];
    
    const mockUsuarios = [
      {
        id_usuario: 1,
        nome_completo: "João Silva",
        email: "joao@email.com"
      },
      // ... mais usuários
    ];
    
    setLivros(mockLivros);
    setUsuarios(mockUsuarios);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    // Implementar lógica de busca
    console.log('Buscando por:', searchTerm);
  };

  const abrirModalEmprestimo = (livroId, livroTitulo) => {
    const livro = livros.find(l => l.id_livro === livroId);
    setSelectedLivro(livro);
    setSelectedUsuario('');
    setShowModal(true);
  };

  const fecharModal = () => {
    setShowModal(false);
    setSelectedLivro(null);
    setSelectedUsuario('');
  };

  const handleEmprestimo = (e) => {
    e.preventDefault();
    if (!selectedLivro || !selectedUsuario) return;

    // Aqui você faria a chamada para a API de empréstimo
    console.log('Realizando empréstimo:', {
      livro_id: selectedLivro.id_livro,
      usuario_id: selectedUsuario
    });

    fecharModal();
  };

  // Filtrar livros baseado na busca
  const filteredLivros = livros.filter(livro => {
    if (!searchTerm) return true;
    
    const term = searchTerm.toLowerCase();
    return (
      livro.titulo.toLowerCase().includes(term) ||
      (livro.autor && livro.autor.toLowerCase().includes(term)) ||
      (livro.categoria_nome && livro.categoria_nome.toLowerCase().includes(term))
    );
  });

  return (
    <div className="book-finder">
      <main>
        <h1>Bem-vindo ao BookFinder</h1>
        <p>
          Encontre seus livros favoritos de forma rápida e fácil. Explore nosso catálogo e 
          descubra novas leituras para todos os gostos.
        </p>

        <div className="search-container">
          <form id="search-form" onSubmit={handleSearch}>
            <input 
              type="text" 
              id="search-input" 
              placeholder="Busque por título, autor ou categoria..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <button type="submit">🔍 Buscar</button>
          </form>
        </div>

        <section id="destaques" className="book-section">
          <h2>📚 Livros em Destaque</h2>
          
          {filteredLivros.length > 0 ? (
            <div className="book-grid">
              {filteredLivros.map(livro => (
                <div 
                  key={livro.id_livro}
                  className="book-card" 
                  data-titulo={livro.titulo.toLowerCase()} 
                  data-categoria={livro.categoria_nome ? livro.categoria_nome.toLowerCase() : ''}
                  data-autor={livro.autor ? livro.autor.toLowerCase() : ''}
                >
                  <div className="book-card-image">
                    {livro.capa ? (
                      <img src={livro.capa} alt={`Capa do livro ${livro.titulo}`} />
                    ) : (
                      <div className="book-placeholder">
                        📖
                      </div>
                    )}
                  </div>
                  <div className="book-card-info">
                    <h3>{livro.titulo}</h3>
                    <p className="book-author">
                      {livro.autor ? livro.autor : 'Autor não informado'}
                    </p>
                    <p className="book-year">
                      {livro.ano_publicacao && livro.ano_publicacao}
                    </p>
                    <p className="book-category">
                      {livro.categoria_nome || livro.genero || ''}
                    </p>
                    
                    <button 
                      className="btn-emprestar" 
                      onClick={() => abrirModalEmprestimo(livro.id_livro, livro.titulo)}
                    >
                      📚 Emprestar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-books">
              <p>📚 {searchTerm ? 'Nenhum livro encontrado para sua busca.' : 'Ainda não há livros cadastrados no sistema.'}</p>
              <a href="/cadastrarlivro" className="btn-primary">
                Cadastrar Primeiro Livro
              </a>
            </div>
          )}
        </section>

        <div className="feature-card">
          <h3>🔍 Buscar Livros Online</h3>
          <p>Explore milhares de livros usando a API do Google Books</p>
          <a href="/buscar_livros" className="btn-primary">Buscar na API</a>
        </div>

        {/* Modal para Empréstimo */}
        {showModal && (
          <div id="modalEmprestimo" className="modal" style={{ display: 'block' }}>
            <div className="modal-content">
              <span className="close" onClick={fecharModal}>&times;</span>
              <h3>📚 Realizar Empréstimo</h3>
              <p id="livroInfo">
                Livro selecionado: {selectedLivro?.titulo}
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
                  >
                    <option value="">Selecione um usuário...</option>
                    {usuarios.map(usuario => (
                      <option key={usuario.id_usuario} value={usuario.id_usuario}>
                        {usuario.nome_completo} - {usuario.email}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn-primary">
                    ✅ Confirmar Empréstimo
                  </button>
                  <button 
                    type="button" 
                    className="btn-secondary" 
                    onClick={fecharModal}
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

export default BookFinder;