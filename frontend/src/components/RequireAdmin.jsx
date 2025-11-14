import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getUser, isAdmin } from '../hooks/useAuth';

export default function RequireAdmin({ children }){
  if(!isAuthenticated()) return <Navigate to="/login" replace />;
  const user = getUser();
  const admin = isAdmin();
  if(!admin) return <Navigate to="/" replace />;
  return children;
}
