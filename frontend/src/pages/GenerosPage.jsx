import React from 'react';

const genres = [
  'Ficção Científica','Fantasia','Romance','Mistério e Suspense','Biografia e Memórias',
  'História','Acadêmico e Técnico','Arte e Fotografia','Autoajuda','Clássicos','Poesia','Terror'
];

export default function GenerosPage(){
  return (
    <div className="container">
      <h1>Explore por Gêneros</h1>
      <p>Navegue por nossas categorias e encontre o livro perfeito para o seu gosto.</p>
      <div className="genre-grid">
        {genres.map(g => (
          <div key={g} className="genre-card"><h3>{g}</h3></div>
        ))}
      </div>
    </div>
  );
}
