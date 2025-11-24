// src/context/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🔄 AuthProvider - Verificando autenticação...');
    
    // Verifica se o usuário está logado usando suas chaves do localStorage
    const token = localStorage.getItem('bf_access');
    const userData = localStorage.getItem('bf_user');
    
    console.log('📋 Dados do localStorage:', { token: !!token, userData: !!userData });
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        console.log('✅ Usuário autenticado encontrado:', parsedUser.nome_completo);
        setIsAuthenticated(true);
        setUser(parsedUser);
      } catch (e) {
        console.error('❌ Erro ao parsear user data:', e);
        logout();
      }
    } else {
      console.log('❌ Nenhum usuário autenticado encontrado');
    }
    setLoading(false);
  }, []);

  const login = (token, userData) => {
    console.log('🔐 Função login chamada:', { token: !!token, user: userData });
    
    // Suas chaves existentes são mantidas
    localStorage.setItem('bf_access', token);
    localStorage.setItem('bf_user', JSON.stringify(userData));
    
    // Chaves adicionais para compatibilidade
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    
    setIsAuthenticated(true);
    setUser(userData);
    
    console.log('✅ Login realizado com sucesso no AuthContext');
  };

  const logout = () => {
    console.log('🚪 Realizando logout...');
    
    // Remove todas as chaves de autenticação
    localStorage.removeItem('bf_access');
    localStorage.removeItem('bf_refresh');
    localStorage.removeItem('bf_user');
    localStorage.removeItem('bf_last_email');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    setIsAuthenticated(false);
    setUser(null);
    
    console.log('✅ Logout realizado com sucesso');
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};