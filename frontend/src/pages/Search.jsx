import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { authFetch } from '../hooks/useAuth';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const API_BASE = 'http://127.0.0.1:5000';

export default function Search() {
  const q = useQuery().get('q') || '';
  const [query, setQuery] = useState(q);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function doSearch(term) {
    if (!term) {
      setResults([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await authFetch(`${API_BASE}/api/buscar-livros?q=${encodeURIComponent(term)}`);
      const json = await res.json();
      if (res.ok) {
        setResults(json.livros || []);
      } else {
        setError(json.error || 'Erro na busca');
        setResults([]);
      }
    } catch (err) {
      setError('Erro de rede: ' + err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(()=>{
    if (q) doSearch(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q]);

  return (
    <div className="busca-container">
      <div className="search-box">
        <input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Buscar livros..." />
        <button className="btn-primary" onClick={() => doSearch(query)}>Buscar</button>
      </div>

      {loading && <div className="loading">Buscando...</div>}
      {error && <div className="error">{error}</div>}

      <div className="livros-grid">
        {results.length === 0 && !loading && <p>Nenhum resultado.</p>}
        {results.map((l, i) => (
          <div key={i} className="livro-card">
            <div className="livro-capa">{l.capa ? <img src={l.capa} alt={l.titulo} /> : <div style={{fontSize:48}}>📚</div>}</div>
            <div className="livro-info">
              <h4>{l.titulo}</h4>
              <p>{l.autores || l.autor}</p>
              <p>{l.editora || l.editora}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
