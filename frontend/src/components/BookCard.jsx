import React from 'react';

export const BookCard = ({ book, onLoan, loading = false, isAdmin = false }) => {
  const handleLoanClick = () => {
    if (isAdmin && book.disponivel !== false) {
      onLoan(book.id_livro, book.titulo);
    }
  };

  const isAvailable = book.disponivel !== false;

  return (
    <div className="book-card">
      <div className="book-card-image">
        {book.capa ? (
          <img
            src={book.capa}
            alt={`Capa do livro ${book.titulo}`}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <span className="text-4xl text-gray-400">📖</span>
          </div>
        )}
        
        {!isAvailable && (
          <div className="book-card-unavailable">
            <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
              EMPRESTADO
            </span>
          </div>
        )}
        
        {isAdmin && isAvailable && (
          <button
            onClick={handleLoanClick}
            disabled={loading}
            className="loan-button"
            title="Realizar empréstimo"
          >
            📚
          </button>
        )}
      </div>
      
      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-gray-900 line-clamp-2 leading-tight">
          {book.titulo}
        </h3>
        
        <p className="text-sm text-gray-600">
          {book.autor || 'Autor não informado'}
        </p>
        
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>{book.ano_publicacao}</span>
          <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
            {book.categoria_nome || book.genero || 'Geral'}
          </span>
        </div>
      </div>
    </div>
  );
};