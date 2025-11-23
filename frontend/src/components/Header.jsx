import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const location = useLocation();
  const pathname = location.pathname;
  const [mobileOpen, setMobileOpen] = useState(false);

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
      <nav className="navbar">
        <div className="container">
          <button className="mobile-toggle" onClick={() => setMobileOpen(s => !s)} aria-label="Abrir menu">
            <i className={`fas ${mobileOpen ? 'fa-times' : 'fa-bars'}`}></i>
          </button>

          <Link to="/" className="logo" title="BookFinder">
            <i className="fas fa-book-open" style={{ marginRight: 8 }}></i>
            <span>BookFinder</span>
          </Link>

          <div className={`nav-links ${mobileOpen ? 'mobile-open' : ''}`}>
            {/* If we're on the content 'home' page, show anchors to sections + Entrar */}
            {pathname === '/home' ? (
              <>
                <a href="#about" onClick={() => setMobileOpen(false)}>Sobre</a>
                <a href="#benefits" onClick={() => setMobileOpen(false)}>Benefícios</a>
                <a href="#catalog" onClick={() => setMobileOpen(false)}>Catálogo</a>
                <Link to="/login" className="btn btn-primary" onClick={() => setMobileOpen(false)}>Entrar</Link>
              </>
            ) : (
              <>
                <Link to="/home" className={isActive('/home') ? 'active' : ''}>Início</Link>
                <Link to="/generos" className={isActive('/generos') ? 'active' : ''}>Gêneros</Link>
                <Link to="/sobre" className={isActive('/sobre') ? 'active' : ''}>Sobre</Link>
                <Link to="/contato" className={isActive('/contato') ? 'active' : ''}>Contato</Link>
                {localStorage.getItem('bf_access') ? (
                  <a href="#" onClick={handleLogout} className="btn btn-outline">Sair</a>
                ) : (
                  <Link to="/login" className={`btn btn-outline ${isActive('/login') ? 'active' : ''}`}>Entre</Link>
                )}
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
