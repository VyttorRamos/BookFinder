import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:5000';

export default function ListarLivro(){
  const [livros, setLivros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await fetch(API_BASE + '/api/livros');
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setLivros(json.livros || []);
        else setError(json.error || 'Erro');
      }catch(err){
        setError(err.message);
      }finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleDelete(id){
    if(!confirm('Confirma exclusão do livro?')) return;
    try{
      const res = await fetch(`${API_BASE}/api/livros/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){
        setLivros(prev => prev.filter(l=> l.id !== id));
        alert(json.message || 'Livro excluído');
      } else {
        alert(json.error || 'Erro ao excluir');
      }
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  return (
    <div>
      <h1>Livros Cadastrados</h1>
      <div style={{marginBottom:20}}><Link to="/livros/cadastrarlivro" className="btn-primary">Cadastrar Novo Livro</Link></div>
      {loading && <div className="loading">Carregando...</div>}
      {error && <div className="error">{error}</div>}
      {!loading && !error && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Autor</th>
                <th>Ano</th>
                <th>Gênero</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {livros.map(l => (
                <tr key={l.id}>
                  <td>{l.id}</td>
                  <td>{l.titulo}</td>
                  <td>{l.autor}</td>
                  <td>{l.ano}</td>
                  <td>{l.categoria}</td>
                  <td className="action-buttons">
                    <Link to={`/livros/editarlivro/${l.id}`} className="edit-btn">Editar</Link>
                    <button onClick={()=>handleDelete(l.id)} className="delete-btn">Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
