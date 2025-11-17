import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function CadastrarEditora(){
  const [nome, setNome] = useState('');
  const [endereco, setEndereco] = useState('');
  const [telefone, setTelefone] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e){
    e.preventDefault();
    if(!nome) return alert('Nome é obrigatório');
    setLoading(true);
    try{
      const res = await authFetch(API_BASE + '/api/editoras', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome, endereco, telefone, email }) });
      const json = await res.json();
      if(res.ok){ alert(json.message || 'Editora cadastrada'); navigate('/editoras/listareditoras'); }
      else alert(json.error || 'Erro ao cadastrar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setLoading(false); }
  }

  return (
    <div className="container contact-container">
      <h1>Cadastrar Editora</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group"><label>Nome da Editora *</label><input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
        <div className="form-group"><label>Endereço</label><input value={endereco} onChange={e=>setEndereco(e.target.value)} /></div>
        <div className="form-group"><label>Telefone</label><input value={telefone} onChange={e=>setTelefone(e.target.value)} /></div>
        <div className="form-group"><label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} /></div>
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={()=>navigate('/editoras/listareditoras')}>Cancelar</button>
          <button type="submit" className="btn-primary" disabled={loading}>{loading? 'Enviando...' : 'Cadastrar Editora'}</button>
        </div>
      </form>
    </div>
  );
}
