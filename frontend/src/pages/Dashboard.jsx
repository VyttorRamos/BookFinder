import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { authFetch } from '../hooks/useAuth';

const API_BASE = 'http://127.0.0.1:5000';

export default function Dashboard(){
  const [stats, setStats] = useState({ livros:0, usuarios:0, emprestimos:0, multas:0 });
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const [livrosRes, usuariosRes, emprestimosRes, multasRes] = await Promise.all([
          fetch(API_BASE + '/api/listar-livros'),
          fetch(API_BASE + '/api/usuarios'),
          fetch(API_BASE + '/api/emprestimos'),
          fetch(API_BASE + '/api/multas')
        ]);

        const livrosJson = await livrosRes.json().catch(()=>({livros:[]}));
        const usuariosJson = await usuariosRes.json().catch(()=>({usuarios:[]}));
        const emprestimosJson = await emprestimosRes.json().catch(()=>({emprestimos:[]}));
        const multasJson = await multasRes.json().catch(()=>({multas:[]}));

        if(!mounted) return;
        setStats({
          livros: (livrosJson.livros || []).length,
          usuarios: (usuariosJson.usuarios || []).length,
          emprestimos: (emprestimosJson.emprestimos || []).length,
          multas: (multasJson.multas || []).length,
        });

        // take latest 8 emprestimos
        setRecent((emprestimosJson.emprestimos || []).slice(0,8));
      }catch(err){
        console.error('Erro carregando dashboard:', err);
      }finally{
        if(mounted) setLoading(false);
      }
    }
    load();
    return ()=> mounted = false;
  },[]);

  return (
    <div className="container">
      <h1>Dashboard</h1>
      <p>Visão geral do sistema</p>

      <div style={{display:'flex',gap:20,flexWrap:'wrap',marginTop:20}}>
        <Link to="/usuarios/listaruser" className="btn-primary" style={{flex:1,textAlign:'center'}}>
          Usuários
          <div style={{fontSize:18,fontWeight:700}}>{stats.usuarios}</div>
        </Link>

        <Link to="/livros/listarlivro" className="btn-primary" style={{flex:1,textAlign:'center'}}>
          Livros
          <div style={{fontSize:18,fontWeight:700}}>{stats.livros}</div>
        </Link>

        <Link to="/emprestimos/listaremprestimos" className="btn-primary" style={{flex:1,textAlign:'center'}}>
          Empréstimos
          <div style={{fontSize:18,fontWeight:700}}>{stats.emprestimos}</div>
        </Link>

        <Link to="/multas/listarmultas" className="btn-primary" style={{flex:1,textAlign:'center'}}>
          Multas
          <div style={{fontSize:18,fontWeight:700}}>{stats.multas}</div>
        </Link>
      </div>

      <section style={{marginTop:30}}>
        <h2>Últimos Empréstimos</h2>
        {loading && <div>Carregando...</div>}
        {!loading && recent.length === 0 && <div>Nenhum empréstimo encontrado.</div>}
        {!loading && recent.length > 0 && (
          <table className="tabela" style={{width:'100%',marginTop:10}}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Livro</th>
                <th>Usuário</th>
                <th>Data Empréstimo</th>
                <th>Data Devolução</th>
              </tr>
            </thead>
            <tbody>
              {recent.map(r => (
                <tr key={r.id_emprestimo || r.id}>
                  <td>{r.id_emprestimo || r.id}</td>
                  <td>{r.titulo || r.livro_titulo || r.livro}</td>
                  <td>{r.nome_usuario || r.usuario_nome || r.usuario}</td>
                  <td>{r.data_emprestimo || r.data || ''}</td>
                  <td>{r.data_devolucao || r.data_prevista || ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

    </div>
  );
}
