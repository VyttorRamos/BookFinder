import React from 'react';
import { useLocation } from 'react-router-dom';

export default function ErrorPage(){
  const loc = useLocation();
  return (
    <div className="container text-container">
      <h1>Ops — Algo deu errado</h1>
      <p>Não foi possível carregar a página <strong>{loc.pathname}</strong>.</p>
      <p>Verifique se o servidor está em execução ou retorne para a <a href="/">página inicial</a>.</p>
    </div>
  );
}
