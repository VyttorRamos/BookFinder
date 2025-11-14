import React, { useState, useEffect, useContext } from 'react';
import { ModalContext } from '../components/ModalProvider';

const API_BASE = 'http://127.0.0.1:5000';

export default function Home() {
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const { openEmprestimo } = useContext(ModalContext);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const res = await fetch(API_BASE + '/api/listar-livros');
        const json = await res.json();
        if (!mounted) return;
        if (res.ok) setBooks(json.livros || []);
        else setBooks([]);
      } catch (err) {
        console.error('Erro ao carregar livros:', err);
        if (mounted) setBooks([]);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

  const filtered = books.filter(b => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return (b.titulo || '').toLowerCase().includes(q) ||
           (b.autor || '').toLowerCase().includes(q) ||
           (b.categoria || '').toLowerCase().includes(q);
  });

  return (
    <div>
      <section className="search-container">
        <form id="search-form" onSubmit={(e)=>e.preventDefault()}>
          <input id="search-input" value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Busque por título, autor ou gênero" />
          <button className="btn-primary" type="submit">Buscar</button>
        </form>
      </section>

      <section className="book-section">
        <h2>Últimos Livros</h2>
        <div className="book-grid">
          {filtered.length === 0 && (
            <div className="no-books"><p>Nenhum livro encontrado.</p></div>
          )}
          {filtered.map((b, idx) => (
            <div key={idx} className="book-card" data-titulo={b.titulo} data-categoria={b.categoria} data-autor={b.autor}>
              <div className="book-card-image">
                {b.capa ? <img src={b.capa} alt={b.titulo} /> : <div className="book-placeholder">📚</div>}
              </div>
              <div className="book-card-info">
                <h3>{b.titulo}</h3>
                <div className="book-author">{b.autor}</div>
                <div className="book-year">{b.ano}</div>
                <button className="btn-emprestar" onClick={() => openEmprestimo(b.id || '', b.titulo)}>Emprestar</button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
