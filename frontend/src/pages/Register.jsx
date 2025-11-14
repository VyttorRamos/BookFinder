import React, { useState, useContext } from 'react';
import { MessageContext } from '../components/MessageProvider';

const API_BASE = 'http://127.0.0.1:5000';

export default function Register(){
  const [nome, setNome] = useState('');
  const [tel, setTel] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [senhaConfirm, setSenhaConfirm] = useState('');
  const [msg, setMsg] = useState(null);
  const { showMessage } = useContext(MessageContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);
    if (!nome || !email || !senha) return setMsg({ text: 'Preencher nome, email e senha!', error: true });
    if (senha !== senhaConfirm) return setMsg({ text: 'As senhas não são iguais.', error: true });
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return setMsg({ text: 'Por favor, insira um email válido.', error: true });

    try {
      const res = await fetch(API_BASE + '/auth/register', { method: 'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ nome_completo: nome, email, senha, telefone: tel }) });
      const json = await res.json();
      if (res.ok) {
        showMessage('Registrado com sucesso. Faça login para continuar!');
        setTimeout(()=>window.location.href='/login', 2000);
      } else {
        showMessage(json.error || json.mensagem || 'Erro no registro', true);
      }
    } catch (err) {
      showMessage('Erro de rede ao registrar. Verifique o CORS.', true);
    }
  };

  return (
    <div className="login-container">
      <h1>Registrar</h1>
      {msg && <div className={msg.error ? 'error' : 'loading'}>{msg.text}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="nome">Nome</label>
          <input id="nome" value={nome} onChange={(e)=>setNome(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="tel">Telefone</label>
          <input id="tel" value={tel} onChange={(e)=>setTel(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="senha">Senha</label>
          <input id="senha" type="password" value={senha} onChange={(e)=>setSenha(e.target.value)} />
        </div>
        <div className="form-group">
          <label htmlFor="senha_confirm">Confirmar Senha</label>
          <input id="senha_confirm" type="password" value={senhaConfirm} onChange={(e)=>setSenhaConfirm(e.target.value)} />
        </div>
        <button type="submit">Registrar</button>
      </form>
    </div>
  );
}
