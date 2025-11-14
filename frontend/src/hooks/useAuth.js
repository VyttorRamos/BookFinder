// Minimal auth helper for frontend
export function getToken(){
  return localStorage.getItem('bf_access');
}

export function getUser(){
  const u = localStorage.getItem('bf_user');
  try{ return u ? JSON.parse(u) : null; }catch(e){ return null; }
}

export function isAuthenticated(){
  return !!getToken();
}

export function isAdmin(){
  const u = getUser();
  if(!u) return false;
  return (u.tipo_usuario && u.tipo_usuario.toLowerCase() === 'admin') || !!u.is_admin;
}

export async function authFetch(url, options={}){
  const token = getToken();
  const headers = options.headers ? {...options.headers} : {};
  if(token) headers['Authorization'] = 'Bearer ' + token;
  return fetch(url, {...options, headers});
}

export function logout(){
  localStorage.removeItem('bf_access');
  localStorage.removeItem('bf_refresh');
  localStorage.removeItem('bf_user');
  window.location.href = '/login';
}
