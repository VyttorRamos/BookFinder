import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ExcluirGenero(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [genero, setGenero] = useState(null);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/generos/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setGenero(json.genero);
        else { alert(json.error||'Não encontrado'); navigate('/generos/listargeneros'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/generos/listargeneros'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[id, navigate]);

  async function handleDelete(){
    if(!confirm('Confirma exclusão do gênero?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/generos/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Excluído'); navigate('/generos/listargeneros'); }
      else alert(json.error||'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Excluir Gênero</h1>
      {genero && (
        <div>
          <p>Tem certeza que deseja excluir o gênero <strong>{genero.nome_genero}</strong>?</p>
          <div className="form-actions">
            <button className="btn-secondary" onClick={()=>navigate('/generos/listargeneros')}>Cancelar</button>
            <button className="delete-btn" onClick={handleDelete}>Excluir</button>
          </div>
        </div>
      )}
    </div>
  );
}
