import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function EditarUser(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [telefone, setTelefone] = useState('');
  const [tipo, setTipo] = useState('aluno');

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(`${API_BASE}/api/usuarios/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok){ const u = json.usuario; setNome(u.nome_completo||''); setEmail(u.email||''); setTelefone(u.telefone||''); setTipo(u.tipo_usuario||'aluno'); }
        else { alert(json.error||'Não encontrado'); navigate('/usuarios/listaruser'); }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/usuarios/listaruser'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[id, navigate]);

  async function handleSubmit(e){
    e.preventDefault();
    if(!nome || !email) return alert('Nome e email são obrigatórios');
    setSaving(true);
    try{
      const res = await authFetch(`${API_BASE}/api/usuarios/${id}`, { method: 'PUT', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome_completo: nome, email, telefone: telefone, tipo_usuario: tipo }) });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Atualizado'); navigate('/usuarios/listaruser'); }
      else alert(json.error||'Erro ao salvar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setSaving(false); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Editar Usuário</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group"><label>Nome</label><input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
        <div className="form-group"><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required /></div>
        <div className="form-group"><label>Telefone</label><input value={telefone} onChange={e=>setTelefone(e.target.value)} /></div>
        <div className="form-group"><label>Tipo</label><select value={tipo} onChange={e=>setTipo(e.target.value)}><option value="aluno">Aluno</option><option value="admin">Admin</option></select></div>
        <div className="form-actions"><button type="button" className="btn-secondary" onClick={()=>navigate('/usuarios/listaruser')}>Cancelar</button><button type="submit" className="btn-primary" disabled={saving}>{saving? 'Salvando...' : 'Salvar'}</button></div>
      </form>
    </div>
  );
}
