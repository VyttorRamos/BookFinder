import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ExcluirUser(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [usuario, setUsuario] = useState(null);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/usuarios/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setUsuario(json.usuario);
        else { alert(json.error||'Não encontrado'); navigate('/usuarios/listaruser'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/usuarios/listaruser'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[id, navigate]);

  async function handleDelete(){
    if(!confirm('Confirma exclusão do usuário?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/usuarios/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Usuário excluído'); navigate('/usuarios/listaruser'); }
      else alert(json.error||'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Excluir Usuário</h1>
      {usuario && (
        <div>
          <p>Deseja realmente excluir o usuário <strong>{usuario.nome_completo}</strong> (ID {usuario.id_usuario})?</p>
          <div className="form-actions">
            <button className="btn-secondary" onClick={()=>navigate('/usuarios/listaruser')}>Cancelar</button>
            <button className="delete-btn" onClick={handleDelete}>Excluir</button>
          </div>
        </div>
      )}
    </div>
  );
}
