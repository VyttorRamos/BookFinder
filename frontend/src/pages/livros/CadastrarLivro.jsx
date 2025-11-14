import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:5000';

export default function CadastrarLivro(){
  const [titulo, setTitulo] = useState('');
  const [isbn, setIsbn] = useState('');
  const [ano, setAno] = useState('');
  const [idEditora, setIdEditora] = useState('');
  const [idCategoria, setIdCategoria] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e){
    e.preventDefault();
    if(!titulo) return alert('Título é obrigatório');
    setLoading(true);
    try{
      const res = await fetch(API_BASE + '/api/livros', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, isbn, ano_publicacao: ano, id_editora: idEditora, id_categoria: idCategoria })
      });
      const json = await res.json();
      if(res.ok){
        alert(json.message || 'Livro cadastrado');
        navigate('/livros/listarlivro');
      } else {
        alert(json.error || 'Erro ao cadastrar');
      }
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setLoading(false); }
  }

  return (
    <div>
      <h1>Cadastrar Livro</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Título</label>
          <input value={titulo} onChange={e=>setTitulo(e.target.value)} />
        </div>
        <div className="form-group">
          <label>ISBN</label>
          <input value={isbn} onChange={e=>setIsbn(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Ano de Publicação</label>
          <input value={ano} onChange={e=>setAno(e.target.value)} />
        </div>
        <div className="form-group">
          <label>ID Editora</label>
          <input value={idEditora} onChange={e=>setIdEditora(e.target.value)} />
        </div>
        <div className="form-group">
          <label>ID Categoria</label>
          <input value={idCategoria} onChange={e=>setIdCategoria(e.target.value)} />
        </div>
        <div className="form-actions">
          <button className="btn-secondary" type="button" onClick={()=>navigate('/livros/listarlivro')}>Cancelar</button>
          <button className="btn-primary" type="submit" disabled={loading}>{loading ? 'Enviando...' : 'Cadastrar'}</button>
        </div>
      </form>
    </div>
  );
}
