import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function EditarEditora(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [nome, setNome] = useState('');
  const [endereco, setEndereco] = useState('');
  const [telefone, setTelefone] = useState('');
  const [email, setEmail] = useState('');

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/editoras/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok){ setNome(json.nome||''); setEndereco(json.endereco||''); setTelefone(json.telefone||''); setEmail(json.email||''); }
        else { alert(json.error||'Não encontrado'); navigate('/editoras/listareditoras'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/editoras/listareditoras'); }
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
      const res = await authFetch(`${API_BASE}/api/editoras/${id}`, { method: 'PUT', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome, endereco, telefone, email }) });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Alterado'); navigate('/editoras/listareditoras'); }
      else alert(json.error||'Erro ao salvar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setSaving(false); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Editar Editora</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group"><label>Nome da Editora *</label><input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
        <div className="form-group"><label>Endereço</label><input value={endereco} onChange={e=>setEndereco(e.target.value)} /></div>
        <div className="form-group"><label>Telefone</label><input value={telefone} onChange={e=>setTelefone(e.target.value)} /></div>
        <div className="form-group"><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} /></div>
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={()=>navigate('/editoras/listareditoras')}>Cancelar</button>
          <button type="submit" className="btn-primary" disabled={saving}>{saving? 'Salvando...' : 'Salvar Alterações'}</button>
        </div>
      </form>
    </div>
  );
}
