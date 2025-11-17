import React, { useState, useEffect, useContext } from 'react';
import { ModalContext } from '../components/ModalProvider';
import { authFetch } from '../hooks/useAuth';
import '../assets/css/home.css';

const API_BASE = 'http://127.0.0.1:5000';

export default function Home() {
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const { openEmprestimo } = useContext(ModalContext);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const res = await authFetch(API_BASE + '/api/listar-livros');
        const json = await res.json();
        if (!mounted) return;
        if (res.ok) setBooks(json.livros || []);
        else setBooks([]);
      } catch (err) {
        console.error('Erro ao carregar livros:', err);
        if (mounted) setBooks([]);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => { mounted = false; };
  }, []);

  const filtered = books.filter(b => {
    const q = query.toLowerCase().trim();
    if (!q) return true;
    return (b.titulo || '').toLowerCase().includes(q) ||
           (b.autor || '').toLowerCase().includes(q) ||
           (b.categoria || '').toLowerCase().includes(q);
  });

  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text fade-in">
              <h1>BookFinder – A Biblioteca Acadêmica do Futuro</h1>
              <p>Uma plataforma inteligente que transforma a maneira como você acessa, pesquisa e gerencia recursos bibliográficos em sua instituição.</p>
              <a href="#catalog" className="btn btn-primary">Explorar Catálogos</a>
            </div>
            <div className="hero-image fade-in">
              <div className="hero-img">
                <i className="fas fa-book" style={{fontSize:300, color:'#4a6cf7'}}></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="section">
        <div className="container">
          <div className="section-title fade-in">
            <h2>Sobre o BookFinder</h2>
            <p>Conheça a plataforma que está revolucionando o acesso ao conhecimento acadêmico</p>
          </div>

          <div className="about-content">
            <div className="about-text fade-in">
              <h3>O que é o BookFinder?</h3>
              <p>O BookFinder é um sistema de gerenciamento de bibliotecas acadêmicas desenvolvido para oferecer uma experiência moderna, intuitiva e eficiente para estudantes, professores e pesquisadores.</p>
              <p>Com tecnologia de ponta e interface amigável, nossa plataforma conecta você aos recursos bibliográficos necessários para seu desenvolvimento acadêmico e pesquisa.</p>

              <div className="features-list">
                <div className="feature-item"><i className="fas fa-check-circle"></i><span>Catálogo digital completo</span></div>
                <div className="feature-item"><i className="fas fa-check-circle"></i><span>Busca inteligente e filtros avançados</span></div>
                <div className="feature-item"><i className="fas fa-check-circle"></i><span>Gestão de empréstimos automatizada</span></div>
                <div className="feature-item"><i className="fas fa-check-circle"></i><span>Acesso remoto 24/7</span></div>
              </div>
            </div>

            <div className="about-image fade-in">
              <div className="about-img">
                <i className="fas fa-laptop-code" style={{fontSize:300, color:'#4a6cf7'}}></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section id="benefits" className="section benefits">
        <div className="container">
          <div className="section-title fade-in">
            <h2>Benefícios</h2>
            <p>Descubra as vantagens de utilizar o BookFinder em sua instituição</p>
          </div>

          <div className="benefits-grid">
            <div className="benefit-card fade-in">
              <div className="benefit-icon"><i className="fas fa-book"></i></div>
              <h3>Acesso Rápido ao Catálogo</h3>
              <p>Encontre qualquer livro, artigo ou recurso em segundos com nossa interface otimizada.</p>
            </div>

            <div className="benefit-card fade-in">
              <div className="benefit-icon"><i className="fas fa-search"></i></div>
              <h3>Busca Inteligente</h3>
              <p>Algoritmos avançados que entendem o contexto da sua pesquisa e sugerem conteúdos relevantes.</p>
            </div>

            <div className="benefit-card fade-in">
              <div className="benefit-icon"><i className="fas fa-mobile-alt"></i></div>
              <h3>Disponível em Qualquer Dispositivo</h3>
              <p>Acesse o sistema de qualquer lugar, a qualquer hora, pelo celular, tablet ou computador.</p>
            </div>

            <div className="benefit-card fade-in">
              <div className="benefit-icon"><i className="fas fa-clock"></i></div>
              <h3>Controle de Empréstimos 24h</h3>
              <p>Renove, reserve e gerencie seus empréstimos de forma simples e automatizada.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Catalog Section */}
      <section id="catalog" className="section">
        <div className="container">
          <div className="section-title fade-in">
            <h2>Catálogos</h2>
            <p>Explore nossa vasta coleção de recursos bibliográficos</p>
          </div>

          <div className="catalog-grid">
            {loading && <div className="loading">Carregando...</div>}
            {!loading && filtered.length === 0 && (
              <>
                <div className="book-card fade-in"><div className="book-cover"><i className="fas fa-atom"></i></div><div className="book-info"><h3>Física Quântica Avançada</h3><p>David J. Griffiths</p><span className="book-category">Ciências Exatas</span></div></div>
                <div className="book-card fade-in"><div className="book-cover"><i className="fas fa-dna"></i></div><div className="book-info"><h3>Biologia Molecular da Célula</h3><p>Bruce Alberts</p><span className="book-category">Ciências Biológicas</span></div></div>
                <div className="book-card fade-in"><div className="book-cover"><i className="fas fa-balance-scale"></i></div><div className="book-info"><h3>Teoria Geral do Direito</h3><p>Hans Kelsen</p><span className="book-category">Direito</span></div></div>
                <div className="book-card fade-in"><div className="book-cover"><i className="fas fa-chart-bar"></i></div><div className="book-info"><h3>Economia: Princípios e Aplicações</h3><p>N. Gregory Mankiw</p><span className="book-category">Economia</span></div></div>
              </>
            )}

            {!loading && filtered.map((b)=> (
              <div key={b.id} className="book-card fade-in">
                <div className="book-cover">{b.capa ? <img src={b.capa} alt={b.titulo} /> : <i className="fas fa-book"></i>}</div>
                <div className="book-info">
                  <h3>{b.titulo}</h3>
                  <p>{b.autor}</p>
                  <span className="book-category">{b.categoria}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="catalog-actions fade-in">
            <a href="#" className="btn btn-primary">Ver Todos os Catálogos</a>
          </div>
        </div>
      </section>

      {/* Login Section */}
      <section id="login" className="login">
        <div className="container">
          <div className="section-title fade-in">
            <h2>Pronto para Explorar?</h2>
            <p>Acesse nossa plataforma e descubra um mundo de conhecimento ao seu alcance</p>
          </div>

          <div className="fade-in">
            <a href="/login" className="btn">Entrar no Sistema</a>
          </div>
        </div>
      </section>
    </div>
  );
}
