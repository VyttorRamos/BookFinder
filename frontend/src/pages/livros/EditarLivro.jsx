import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:5000';

export default function EditarLivro(){
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [livro, setLivro] = useState(null);
  const [titulo, setTitulo] = useState('');
  const [isbn, setIsbn] = useState('');
  const [ano, setAno] = useState('');
  const [idEditora, setIdEditora] = useState('');
  const [idCategoria, setIdCategoria] = useState('');

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await fetch(`${API_BASE}/api/livros/${id}`);
        const json = await res.json();
        if(!mounted) return;
        if(res.ok){
          setLivro(json);
          setTitulo(json.titulo || '');
          setIsbn(json.isbn || '');
          setAno(json.ano || '');
          setIdEditora(json.id_editora || '');
          setIdCategoria(json.id_categoria || '');
        } else {
          alert(json.error || 'Não encontrado');
          navigate('/livros/listarlivro');
        }
      }catch(err){ alert('Erro de rede: '+err.message); navigate('/livros/listarlivro'); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  }, [id, navigate]);

  async function handleSubmit(e){
    e.preventDefault();
    if(!titulo) return alert('Título é obrigatório');
    setSaving(true);
    try{
      const res = await fetch(`${API_BASE}/api/livros/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, isbn, ano_publicacao: ano, id_editora: idEditora, id_categoria: idCategoria })
      });
      const json = await res.json();
      if(res.ok){ alert(json.message || 'Atualizado'); navigate('/livros/listarlivro'); }
      else alert(json.error || 'Erro ao atualizar');
    }catch(err){ alert('Erro de rede: '+err.message); }
    finally{ setSaving(false); }
  }

  if(loading) return <div className="loading">Carregando...</div>;

  return (
    <div>
      <h1>Editar Livro</h1>
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
          <label>Ano</label>
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
          <button type="button" className="btn-secondary" onClick={()=>navigate('/livros/listarlivro')}>Cancelar</button>
          <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</button>
        </div>
      </form>
    </div>
  );
}
