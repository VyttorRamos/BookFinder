import React, { useEffect, useState } from 'react';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ListarGeneros(){
  const [generos, setGeneros] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(API_BASE + '/api/generos');
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setGeneros(json.generos || []);
        else setGeneros([]);
      }catch(err){ setGeneros([]); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleDelete(id){
    if(!confirm('Confirma exclusão do gênero?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/generos/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Gênero excluído'); setGeneros(prev=> prev.filter(g=> g.id_genero !== id)); }
      else alert(json.error||'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  return (
    <div className="container">
      <h1>Gêneros</h1>
      {loading && <div className="loading">Carregando...</div>}
      {!loading && (
        <div className="genre-grid">
          {generos.map(g => (
            <div key={g.id_genero} className="genre-card">
              <h3>{g.nome_genero}</h3>
              <div style={{marginTop:10}}>
                <button className="edit-btn" onClick={()=> window.location.href = `/generos/editargenero/${g.id_genero}`}>Editar</button>
                <button className="delete-btn" onClick={()=>handleDelete(g.id_genero)}>Excluir</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
