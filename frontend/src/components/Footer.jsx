import React from 'react';

export default function Footer() {
  return (
    <footer>
      <div className="footer-content">
        <p>© {new Date().getFullYear()} BookFinder. Todos os direitos reservados.</p>
        <p>Sua biblioteca acadêmica para encontrar as melhores leituras.</p>
        <ul className="footer-links">
          <li><a href="/termos">Termos de Serviço</a></li>
          <li><a href="/privacidade">Política de Privacidade</a></li>
          <li><a href="/contato">Fale Conosco</a></li>
        </ul>
      </div>
    </footer>
  );
}
