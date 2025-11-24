import React, { useState } from 'react';

export const LoanModal = ({ 
  open, 
  onOpenChange, 
  bookTitle, 
  bookId, 
  usuarios = [], 
  onConfirm,
  loading = false 
}) => {
  const [selectedUsuario, setSelectedUsuario] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedUsuario && bookId) {
      onConfirm(bookId, selectedUsuario);
    }
  };

  const handleClose = () => {
    setSelectedUsuario('');
    onOpenChange(false);
  };

  if (!open) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">📚 Realizar Empréstimo</h3>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            ✕
          </button>
        </div>
        
        <p className="text-gray-600 mb-6">
          Livro selecionado: <strong className="text-gray-900">{bookTitle}</strong>
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="usuarioSelect" className="block text-sm font-medium text-gray-700 mb-2">
              Selecione o usuário:
            </label>
            <select
              id="usuarioSelect"
              value={selectedUsuario}
              onChange={(e) => setSelectedUsuario(e.target.value)}
              required
              disabled={loading || usuarios.length === 0}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
            >
              <option value="">Selecione um usuário...</option>
              {usuarios.length > 0 ? (
                usuarios.map(usuario => (
                  <option key={usuario.id_usuario} value={usuario.id_usuario}>
                    {usuario.nome_completo} - {usuario.email}
                  </option>
                ))
              ) : (
                <option value="" disabled>
                  Nenhum usuário disponível
                </option>
              )}
            </select>
            
            {usuarios.length === 0 && (
              <p className="text-sm text-gray-500 mt-2">
                Apenas administradores podem visualizar a lista de usuários
              </p>
            )}
          </div>
          
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading || usuarios.length === 0 || !selectedUsuario}
              className="btn-primary flex-1"
            >
              {loading ? '⏳ Processando...' : '✅ Confirmar Empréstimo'}
            </button>
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="btn-secondary flex-1"
            >
              ❌ Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};