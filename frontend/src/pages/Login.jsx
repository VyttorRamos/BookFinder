import React, { useState, useEffect, useContext } from 'react';
import { MessageContext } from '../components/MessageProvider';

const API_BASE = 'http://127.0.0.1:5000';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [msg, setMsg] = useState(null);
  const { showMessage } = useContext(MessageContext);

  useEffect(() => {
    const last = localStorage.getItem('bf_last_email');
    if (last) setEmail(last);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);
    if (!email || !senha) return setMsg({ text: 'Preencha email e senha.', error: true });

    try {
      const res = await fetch(API_BASE + '/auth/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
      });
      const json = await res.json();
      if (res.ok) {
        if (json.access_token) {
          localStorage.setItem('bf_access', json.access_token);
          localStorage.setItem('bf_refresh', json.refresh_token || '');
          // salvar usuário para checagens rápidas no frontend
          try{ localStorage.setItem('bf_user', JSON.stringify(json.user || {})); }catch(e){}
        }
        localStorage.setItem('bf_last_email', email);
        showMessage('Login realizado com sucesso.');
        setTimeout(() => {
          if (json.user && (json.user.tipo_usuario === 'admin' || json.is_admin)) window.location.href = '/dashboard';
          else window.location.href = '/';
        }, 700);
      } else {
        showMessage(json.error || json.message || 'Credenciais inválidas', true);
      }
    } catch (err) {
      showMessage('Erro de rede ao logar. Verifique o backend e CORS.', true);
    }
  };

  return (
    <div className="login-container">
      <h1>Entrar</h1>
      {msg && <div className={msg.error ? 'error' : 'loading'}>{msg.text}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="senha">Senha</label>
          <input id="senha" type="password" value={senha} onChange={(e)=>setSenha(e.target.value)} />
        </div>
        <button type="submit">Entrar</button>
      </form>
      <p>Não tem conta? <a href="/register">Registre-se</a></p>
    </div>
  );
}
