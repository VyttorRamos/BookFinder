import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { MessageContext } from '../components/MessageProvider';
import { useAuth } from '../context/AuthContext';

const API_BASE = 'http://127.0.0.1:5000';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);
  const { showMessage } = useContext(MessageContext);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const last = localStorage.getItem('bf_last_email');
    if (last) setEmail(last);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);
    setLoading(true);
    
    if (!email || !senha) {
      setMsg({ text: 'Preencha email e senha.', error: true });
      setLoading(false);
      return;
    }

    try {
      console.log('📤 Enviando requisição de login...', { email });
      
      const res = await fetch(API_BASE + '/auth/login', {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
      });
      
      console.log('📥 Resposta recebida:', res.status, res.statusText);
      
      const json = await res.json();
      console.log('📋 Dados da resposta:', json);
      
      if (res.ok) {
        console.log('✅ Login bem-sucedido');
        
        // Verifica a estrutura da resposta
        const accessToken = json.access_token || json.token;
        const userData = json.user || {};
        
        if (!accessToken) {
          console.error('❌ Token não encontrado na resposta');
          showMessage('Erro: Token de acesso não recebido', true);
          return;
        }
        
        // Salva os tokens no localStorage
        localStorage.setItem('bf_access', accessToken);
        localStorage.setItem('bf_refresh', json.refresh_token || '');
        localStorage.setItem('bf_user', JSON.stringify(userData));
        localStorage.setItem('bf_last_email', email);
        
        console.log('🔐 Tokens salvos no localStorage');
        
        // Usa o AuthContext para fazer login
        login(accessToken, userData);
        
        showMessage('Login realizado com sucesso!');
        
        // Redireciona após um breve delay
        setTimeout(() => {
          console.log('🔄 Redirecionando...');
          if (userData.tipo_usuario === 'admin' || json.is_admin) {
            navigate('/dashboard');
          } else {
            navigate('/home');
          }
        }, 1000);
        
      } else {
        console.error('❌ Erro no login:', json.error || json.message);
        showMessage(json.error || json.message || 'Credenciais inválidas', true);
      }
    } catch (err) {
      console.error('💥 Erro de rede:', err);
      showMessage('Erro de conexão com o servidor. Verifique se o backend está rodando.', true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Entrar no BookFinder</h1>
      {msg && (
        <div className={`message ${msg.error ? 'error' : 'success'}`}>
          {msg.text}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input 
            id="email" 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="senha">Senha</label>
          <input 
            id="senha" 
            type="password" 
            value={senha} 
            onChange={(e) => setSenha(e.target.value)} 
            required
            disabled={loading}
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
      
      <p>Não tem conta? <Link to="/register">Registre-se</Link></p>
      
      {/* Debug info */}
      <div style={{ marginTop: '20px', padding: '10px', background: '#f5f5f5', borderRadius: '5px', fontSize: '12px' }}>
        <strong>Debug Info:</strong>
        <div>Backend: {API_BASE}</div>
        <div>Email salvo: {localStorage.getItem('bf_last_email') || 'Nenhum'}</div>
        <div>Token: {localStorage.getItem('bf_access') ? 'Presente' : 'Ausente'}</div>
      </div>
    </div>
  );
}