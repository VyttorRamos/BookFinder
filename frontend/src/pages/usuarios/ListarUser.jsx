import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ListarUser(){
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(API_BASE + '/api/usuarios');
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setUsuarios(json.usuarios || []);
        else setUsuarios([]);
      }catch(err){ setUsuarios([]); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleDelete(id){
    if(!confirm('Confirma exclusão do usuário?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/usuarios/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Usuário deletado'); setUsuarios(prev=> prev.filter(u=> u.id !== id)); }
      else alert(json.error||'Erro ao excluir');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  return (
    <div className="container">
      <h1>Usuários Cadastrados</h1>
      {loading && <div className="loading">Carregando...</div>}
      {!loading && (
        <div className="table-container">
          <table>
            <thead><tr><th>ID</th><th>Nome</th><th>Email</th><th>Ações</th></tr></thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id}><td>{u.id}</td><td>{u.nome_completo}</td><td>{u.email}</td>
                  <td className="action-buttons">
                    <Link to={`/usuarios/editaruser/${u.id}`} className="edit-btn">Editar</Link>
                    <button className="delete-btn" onClick={()=>handleDelete(u.id)}>Excluir</button>
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
