import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function EditarGenero(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/generos/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok){ setNome(json.genero.nome_genero||''); setDescricao(json.genero.descricao||''); }
        else { alert(json.error||'Não encontrado'); navigate('/generos/listargeneros'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/generos/listargeneros'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[id, navigate]);

  async function handleSubmit(e){
    e.preventDefault();
    if(!nome) return alert('Nome é obrigatório');
    setSaving(true);
    try{
      const res = await authFetch(`${API_BASE}/api/generos/${id}`, { method: 'PUT', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome_genero: nome, descricao }) });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Atualizado'); navigate('/generos/listargeneros'); }
      else alert(json.error||'Erro ao salvar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setSaving(false); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Editar Gênero</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group"><label>Nome do Gênero</label><input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
        <div className="form-group"><label>Descrição</label><textarea value={descricao} onChange={e=>setDescricao(e.target.value)} /></div>
        <div className="form-actions"><button type="button" className="btn-secondary" onClick={()=>navigate('/generos/listargeneros')}>Cancelar</button><button type="submit" className="btn-primary" disabled={saving}>{saving? 'Salvando...' : 'Salvar'}</button></div>
      </form>
    </div>
  );
}
