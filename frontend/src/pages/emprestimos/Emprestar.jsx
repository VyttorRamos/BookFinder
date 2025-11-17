import React, { useEffect, useState } from 'react';
import { authFetch } from '../../hooks/useAuth';
const API_BASE = 'http://127.0.0.1:5000';

export default function Emprestar(){
  const [livros, setLivros] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [idLivro, setIdLivro] = useState('');
  const [idUsuario, setIdUsuario] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const [r1, r2] = await Promise.all([
          authFetch(API_BASE + '/api/listar-livros'),
          authFetch(API_BASE + '/api/usuarios')
        ]);
        const j1 = await r1.json();
        const j2 = await r2.json();
        if(!mounted) return;
        setLivros(r1.ok ? (j1.livros||[]) : []);
        setUsuarios(r2.ok ? (j2.usuarios||[]) : []);
        if(r1.ok && j1.livros && j1.livros[0]) setIdLivro(j1.livros[0].id);
        if(r2.ok && j2.usuarios && j2.usuarios[0]) setIdUsuario(j2.usuarios[0].id);
      }catch(err){ console.error(err); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleSubmit(e){
    e.preventDefault();
    if(!idLivro || !idUsuario) return alert('Selecione livro e usuário');
    setSending(true);
    try{
      const res = await authFetch(API_BASE + '/api/emprestimos', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ id_livro: idLivro, id_usuario: idUsuario }) });
      const json = await res.json();
      if(res.ok){ alert(json.message || 'Empréstimo realizado'); window.location.href = '/emprestimos/listaremprestimos'; }
      else alert(json.error || 'Erro ao emprestar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setSending(false); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="container contact-container">
      <h1>Realizar Empréstimo</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Livro</label>
          <select value={idLivro} onChange={e=>setIdLivro(e.target.value)}>
            {livros.map(l=> <option key={l.id} value={l.id}>{l.titulo}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label>Usuário</label>
          <select value={idUsuario} onChange={e=>setIdUsuario(e.target.value)}>
            {usuarios.map(u=> <option key={u.id} value={u.id}>{u.nome_completo}</option>)}
          </select>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={sending}>{sending? 'Enviando...' : 'Emprestar'}</button>
        </div>
      </form>
    </div>
  );
}
