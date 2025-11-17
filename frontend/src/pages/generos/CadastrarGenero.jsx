import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function CadastrarGenero(){
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e){
    e.preventDefault();
    if(!nome) return alert('Nome é obrigatório');
    setLoading(true);
    try{
      const res = await authFetch(API_BASE + '/api/generos', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome_genero: nome, descricao }) });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Gênero criado'); navigate('/generos/listargeneros'); }
      else alert(json.error||'Erro ao criar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setLoading(false); }
  }

  return (
    <div className="container contact-container">
      <h1>Cadastrar Gênero</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group"><label>Nome do Gênero</label><input value={nome} onChange={e=>setNome(e.target.value)} required /></div>
        <div className="form-group"><label>Descrição</label><textarea value={descricao} onChange={e=>setDescricao(e.target.value)} /></div>
        <div className="form-actions"><button type="button" className="btn-secondary" onClick={()=>navigate('/generos/listargeneros')}>Cancelar</button><button type="submit" className="btn-primary" disabled={loading}>{loading? 'Enviando...' : 'Cadastrar'}</button></div>
      </form>
    </div>
  );
}
