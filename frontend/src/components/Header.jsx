import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const location = useLocation();
  const pathname = location.pathname;

  const isActive = (p) => {
    if (p === '/' && (pathname === '/' || pathname === '')) return true;
    return pathname === p;
  };

  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.removeItem('bf_access');
    localStorage.removeItem('bf_refresh');
    window.location.href = '/';
  };

  return (
    <header>
      <nav>
        <div className="logo">
          <Link to="/" title="BookFinder">
            <img src="/static/img/BookFinderIcon.png" alt="Logo BookFinder" />
          </Link>
        </div>
        <ul className="menu">
          <li><Link to="/" className={isActive('/') ? 'active' : ''}>Início</Link></li>
          <li><Link to="/generos" className={isActive('/generos') ? 'active' : ''}>Gêneros</Link></li>
          <li><Link to="/sobre" className={isActive('/sobre') ? 'active' : ''}>Sobre</Link></li>
          <li><Link to="/contato" className={isActive('/contato') ? 'active' : ''}>Contato</Link></li>
          {localStorage.getItem('bf_access') ? (
            <li><a href="#" onClick={handleLogout}>Sair</a></li>
          ) : (
            <li><Link to="/login" className={isActive('/login') ? 'active' : ''}>Entre</Link></li>
          )}
        </ul>
      </nav>
    </header>
  );
}
