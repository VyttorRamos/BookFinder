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

  let response = await fetch(url, {...options, headers});

  // If unauthorized, try refresh once
  if (response.status === 401) {
    const refresh = localStorage.getItem('bf_refresh');
    if (!refresh) {
      logout();
      return response;
    }

    try {
      const rr = await fetch('http://127.0.0.1:5000/auth/refresh', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + refresh }
      });

      if (rr.ok) {
        const j = await rr.json();
        if (j.access_token) {
          localStorage.setItem('bf_access', j.access_token);
          // retry original request with new token
          const newHeaders = {...headers, Authorization: 'Bearer ' + j.access_token};
          response = await fetch(url, {...options, headers: newHeaders});
        }
      } else {
        // refresh failed -> force logout
        logout();
      }
    } catch (err) {
      logout();
    }
  }

  return response;
}

export function logout(){
  localStorage.removeItem('bf_access');
  localStorage.removeItem('bf_refresh');
  localStorage.removeItem('bf_user');
  window.location.href = '/login';
}
