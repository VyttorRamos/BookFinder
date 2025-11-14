import React, { createContext, useCallback, useState } from 'react';

export const ModalContext = createContext({ openEmprestimo: () => {} });

export default function ModalProvider({ children }) {
  const [visible, setVisible] = useState(false);
  const [livro, setLivro] = useState({ id: '', titulo: '' });

  const openEmprestimo = useCallback((livroId, livroTitulo) => {
    setLivro({ id: livroId, titulo: livroTitulo });
    setVisible(true);
  }, []);

  const close = useCallback(() => {
    setVisible(false);
    setLivro({ id: '', titulo: '' });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = e.target;
    const livroId = form.livro_id.value;
    const usuarioId = form.usuario_id.value;
    try {
      const response = await fetch('/emprestar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `id_livro=${encodeURIComponent(livroId)}&id_usuario=${encodeURIComponent(usuarioId)}`,
      });
      if (response.ok) {
        alert('✅ Empréstimo realizado com sucesso!');
        close();
      } else {
        const error = await response.text();
        alert('❌ Erro ao realizar empréstimo: ' + error);
      }
    } catch (err) {
      alert('❌ Erro de rede: ' + err);
    }
  };

  return (
    <ModalContext.Provider value={{ openEmprestimo }}>
      {children}

      {visible && (
        <div className="modal" style={{ display: 'block' }}>
          <div className="modal-content">
            <span className="close" onClick={close}>&times;</span>
            <h3>Empréstimo</h3>
            <p id="livroInfo">Livro: {livro.titulo}</p>
            <form id="formEmprestimo" onSubmit={handleSubmit}>
              <input type="hidden" name="livro_id" value={livro.id} />
              <div className="form-group">
                <label htmlFor="usuario_id">ID do Usuário</label>
                <input id="usuario_id" name="usuario_id" required />
              </div>
              <div className="form-actions">
                <button type="button" className="btn-secondary" onClick={close}>Cancelar</button>
                <button type="submit" className="btn-primary">Confirmar Empréstimo</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </ModalContext.Provider>
  );
}
