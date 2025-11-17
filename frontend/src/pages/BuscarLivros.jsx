import React from 'react';
import Search from './Search';

export default function BuscarLivros(){
  // Reuse the Search component which implements the Google Books search behavior
  return (
    <div className="busca-container">
      <h1>🔍 Buscar Livros Online</h1>
      <Search />
    </div>
  );
}
