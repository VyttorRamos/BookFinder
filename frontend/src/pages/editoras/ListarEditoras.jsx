import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ListarEditoras(){
  const [editoras, setEditoras] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(API_BASE + '/api/editoras');
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setEditoras(json.editoras || []);
        else setEditoras([]);
      }catch(err){ setEditoras([]); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleDelete(id){
    if(!confirm('Confirma exclusão da editora?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/editoras/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ setEditoras(prev => prev.filter(e => e.id !== id)); alert(json.message || 'Editora excluída'); }
      else alert(json.error || 'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  return (
    <div className="container">
      <h1>Editoras Cadastradas</h1>
      <div style={{marginBottom:20}}><Link to="/editoras/cadastrareditora" className="btn-primary">Cadastrar Editora</Link></div>
      {loading && <div className="loading">Carregando...</div>}
      {!loading && editoras.length === 0 && (
        <div className="no-data">
          <p>Nenhuma editora cadastrada.</p>
        </div>
      )}
      {!loading && editoras.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr><th>ID</th><th>Nome</th><th>Endereço</th><th>Telefone</th><th>Email</th><th>Ações</th></tr>
            </thead>
            <tbody>
              {editoras.map(e => (
                <tr key={e.id}>
                  <td>{e.id}</td>
                  <td>{e.nome}</td>
                  <td>{e.endereco || '-'}</td>
                  <td>{e.telefone || '-'}</td>
                  <td>{e.email || '-'}</td>
                  <td className="action-buttons">
                    <Link to={`/editoras/editareditora/${e.id}`} className="edit-btn">Editar</Link>
                    <button onClick={()=>handleDelete(e.id)} className="delete-btn">Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
