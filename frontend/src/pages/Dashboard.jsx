import React from 'react';

export default function Dashboard(){
  return (
    <div className="container">
      <h1>Dashboard Admin</h1>
      <p>Selecione o que deseja fazer no sistema:</p>

      <div className="genre-grid">
        <div className="genre-card">
          <h3>Usuários</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/usuarios/listaruser">Listar</option>
            <option value="/usuarios/listaruser">Editar</option>
            <option value="/usuarios/listaruser">Excluir</option>
          </select>
        </div>

        <div className="genre-card">
          <h3>Livros</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/livros/listarlivro">Listar</option>
            <option value="/livros/cadastrarlivro">Cadastrar</option>
            <option value="/livros/listarlivro">Editar</option>
            <option value="/livros/listarlivro">Excluir</option>
          </select>
        </div>

        <div className="genre-card">
          <h3>Gêneros</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/generos/listargeneros">Listar</option>
            <option value="/generos/cadastrargenero">Cadastrar</option>
            <option value="/generos/listargeneros">Editar</option>
            <option value="/generos/listargeneros">Excluir</option>
          </select>
        </div>

        <div className="genre-card">
          <h3>Editoras</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/editoras/listareditoras">Listar</option>
            <option value="/editoras/cadastrareditora">Cadastrar</option>
            <option value="/editoras/listareditoras">Editar</option>
            <option value="/editoras/listareditoras">Excluir</option>
          </select>
        </div>

        <div className="genre-card">
          <h3>Empréstimos</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/emprestimos/listaremprestimos">Listar Empréstimos</option>
            <option value="/emprestimos/emprestar">Realizar Empréstimo</option>
            <option value="/emprestimos/listaremprestimos">Devolução</option>
            <option value="/emprestimos/listaremprestimos">Renovação</option>
            <option value="/emprestimos/listaratrasados">Atrasados</option>
          </select>
        </div>

        <div className="genre-card">
          <h3>Multas</h3>
          <select className="admin-select">
            <option value="" disabled defaultValue>Escolha uma ação</option>
            <option value="/multas/listarmultas">Listar Multas</option>
            <option value="/multas/listarmultas">Remover Multa</option>
          </select>
        </div>
      </div>
    </div>
  );
}
