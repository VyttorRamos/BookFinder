import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ExcluirEditora(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [editora, setEditora] = useState(null);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/editoras/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setEditora(json);
        else { alert(json.error||'Não encontrado'); navigate('/editoras/listareditoras'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/editoras/listareditoras'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  }, [id, navigate]);

  async function handleDelete(){
    if(!confirm('Confirma exclusão da editora?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/editoras/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Editora excluída'); navigate('/editoras/listareditoras'); }
      else alert(json.error||'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Excluir Editora</h1>
      {editora && (
        <div>
          <p>Tem certeza que deseja excluir a editora <strong>"{editora.nome}"</strong>?</p>
          <div className="form-actions">
            <button className="btn-secondary" onClick={()=>navigate('/editoras/listareditoras')}>Cancelar</button>
            <button className="delete-btn" onClick={handleDelete}>Confirmar Exclusão</button>
          </div>
        </div>
      )}
    </div>
  );
}
