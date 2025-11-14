import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:5000';

export default function ExcluirLivro(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [livro, setLivro] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await fetch(`${API_BASE}/api/livros/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setLivro(json);
        else { alert(json.error || 'Não encontrado'); navigate('/livros/listarlivro'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/livros/listarlivro'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  }, [id, navigate]);

  async function handleDelete(){
    if(!confirm('Confirma exclusão do livro?')) return;
    try{
      const res = await fetch(`${API_BASE}/api/livros/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message || 'Excluído'); navigate('/livros/listarlivro'); }
      else alert(json.error || 'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div>
      <h1>Excluir Livro</h1>
      {livro && (
        <div>
          <p>Deseja realmente excluir o livro <strong>{livro.titulo}</strong> (ID {livro.id})?</p>
          <div className="form-actions">
            <button className="btn-secondary" onClick={()=>navigate('/livros/listarlivro')}>Cancelar</button>
            <button className="btn-primary" onClick={handleDelete}>Excluir</button>
          </div>
        </div>
      )}
    </div>
  );
}
