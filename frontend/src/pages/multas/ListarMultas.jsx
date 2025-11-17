import React, { useEffect, useState } from 'react';
import { authFetch } from '../../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function ListarMultas(){
  const [multas, setMultas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const res = await authFetch(API_BASE + '/api/multas');
        const json = await res.json();
        if(!mounted) return;
        if(res.ok) setMultas(json.multas || []);
        else setMultas([]);
      }catch(err){ setMultas([]); }
      finally{ if(mounted) setLoading(false); }
    }
    load();
    return ()=> mounted = false;
  },[]);

  async function handleRemove(id){
    if(!confirm('Confirma remoção desta multa?')) return;
    try{
      const res = await authFetch(`${API_BASE}/api/multas/${id}`, { method: 'DELETE' });
      const json = await res.json();
      if(res.ok){ alert(json.message||'Removida'); setMultas(prev=>prev.filter(m=> m.id_multa !== id)); }
      else alert(json.error||'Erro');
    }catch(err){ alert('Erro de rede: '+err.message); }
  }

  return (
    <div className="container">
      <h1>Multas Cadastradas</h1>
      {loading && <div className="loading">Carregando...</div>}
      {!loading && multas.length === 0 && <div className="no-data"><p>Nenhuma multa cadastrada.</p></div>}
      {!loading && multas.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr><th>ID</th><th>Livro</th><th>Usuário</th><th>Valor</th><th>Status</th><th>Data</th><th>Ações</th></tr>
            </thead>
            <tbody>
              {multas.map(m => (
                <tr key={m.id_multa}>
                  <td>{m.id_multa}</td>
                  <td>{m.titulo}</td>
                  <td>{m.nome_completo}</td>
                  <td>{m.valor}</td>
                  <td>{m.status_multa}</td>
                  <td>{m.dt_criacao}</td>
                  <td>{m.status_multa === 'pendente' ? <button className="delete-btn" onClick={()=>handleRemove(m.id_multa)}>Remover</button> : <span className="disabled-btn">Já processada</span> }</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
