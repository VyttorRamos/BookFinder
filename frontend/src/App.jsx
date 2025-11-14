import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import MessageProvider from './components/MessageProvider';
import ModalProvider from './components/ModalProvider';
import AdminSelects from './components/AdminSelects';
import CaptchaHandler from './components/CaptchaHandler';
import RequireAdmin from './components/RequireAdmin';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Search from './pages/Search';
import BuscarLivros from './pages/BuscarLivros';
import Contato from './pages/Contato';
import Dashboard from './pages/Dashboard';
import GenerosPage from './pages/GenerosPage';
import Sobre from './pages/Sobre';
import Privacidade from './pages/Privacidade';
import Termos from './pages/Termos';
import ErrorPage from './pages/ErrorPage';

// editoras
import CadastrarEditora from './pages/editoras/CadastrarEditora';
import EditarEditora from './pages/editoras/EditarEditora';
import ExcluirEditora from './pages/editoras/ExcluirEditora';
import ListarEditoras from './pages/editoras/ListarEditoras';

// emprestimos
import Devolver from './pages/emprestimos/Devolver';
import Emprestar from './pages/emprestimos/Emprestar';
import ListarAtrasados from './pages/emprestimos/ListarAtrasados';
import ListarEmprestimos from './pages/emprestimos/ListarEmprestimos';
import Renovar from './pages/emprestimos/Renovar';

// generos subpages
import CadastrarGenero from './pages/generos/CadastrarGenero';
import EditarGenero from './pages/generos/EditarGenero';
import ExcluirGenero from './pages/generos/ExcluirGenero';
import ListarGeneros from './pages/generos/ListarGeneros';

// livros
import CadastrarLivro from './pages/livros/CadastrarLivro';
import EditarLivro from './pages/livros/EditarLivro';
import ExcluirLivro from './pages/livros/ExcluirLivro';
import ListarLivro from './pages/livros/ListarLivro';

// multas
import ListarMultas from './pages/multas/ListarMultas';
import RemoverMulta from './pages/multas/RemoverMulta';

// usuarios
import EditarUser from './pages/usuarios/EditarUser';
import ExcluirUser from './pages/usuarios/ExcluirUser';
import ListarUser from './pages/usuarios/ListarUser';

export default function App() {
  return (
    <MessageProvider>
      <ModalProvider>
        <div className="app-root">
          <AdminSelects />
          <CaptchaHandler />
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/home" element={<Navigate to="/" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/busca" element={<Search />} />
              <Route path="/buscar_livros" element={<BuscarLivros />} />
              <Route path="/contato" element={<Contato />} />
              <Route path="/dashboard" element={<RequireAdmin><Dashboard /></RequireAdmin>} />
              <Route path="/generos" element={<GenerosPage />} />
              <Route path="/sobre" element={<Sobre />} />
              <Route path="/privacidade" element={<Privacidade />} />
              <Route path="/termos" element={<Termos />} />
              <Route path="/error" element={<ErrorPage />} />

              {/* editoras */}
              <Route path="/editoras/cadastrareditora" element={<RequireAdmin><CadastrarEditora /></RequireAdmin>} />
              <Route path="/editoras/editareditora" element={<RequireAdmin><EditarEditora /></RequireAdmin>} />
              <Route path="/editoras/excluireditora" element={<RequireAdmin><ExcluirEditora /></RequireAdmin>} />
              <Route path="/editoras/listareditoras" element={<RequireAdmin><ListarEditoras /></RequireAdmin>} />

              {/* emprestimos */}
              <Route path="/emprestimos/devolver" element={<RequireAdmin><Devolver /></RequireAdmin>} />
              <Route path="/emprestimos/emprestar" element={<RequireAdmin><Emprestar /></RequireAdmin>} />
              <Route path="/emprestimos/listaratrasados" element={<RequireAdmin><ListarAtrasados /></RequireAdmin>} />
              <Route path="/emprestimos/listaremprestimos" element={<RequireAdmin><ListarEmprestimos /></RequireAdmin>} />
              <Route path="/emprestimos/renovar" element={<RequireAdmin><Renovar /></RequireAdmin>} />

              {/* generos subpages */}
              <Route path="/generos/cadastrargenero" element={<RequireAdmin><CadastrarGenero /></RequireAdmin>} />
              <Route path="/generos/editargenero" element={<RequireAdmin><EditarGenero /></RequireAdmin>} />
              <Route path="/generos/excluirgenero" element={<RequireAdmin><ExcluirGenero /></RequireAdmin>} />
              <Route path="/generos/listargeneros" element={<RequireAdmin><ListarGeneros /></RequireAdmin>} />

              {/* livros */}
              <Route path="/livros/cadastrarlivro" element={<RequireAdmin><CadastrarLivro /></RequireAdmin>} />
              <Route path="/livros/editarlivro/:id" element={<RequireAdmin><EditarLivro /></RequireAdmin>} />
              <Route path="/livros/excluirlivro/:id" element={<RequireAdmin><ExcluirLivro /></RequireAdmin>} />
              <Route path="/livros/listarlivro" element={<RequireAdmin><ListarLivro /></RequireAdmin>} />

              {/* multas */}
              <Route path="/multas/listarmultas" element={<RequireAdmin><ListarMultas /></RequireAdmin>} />
              <Route path="/multas/removermulta" element={<RequireAdmin><RemoverMulta /></RequireAdmin>} />

              {/* usuarios */}
              <Route path="/usuarios/editaruser" element={<RequireAdmin><EditarUser /></RequireAdmin>} />
              <Route path="/usuarios/excluiruser" element={<RequireAdmin><ExcluirUser /></RequireAdmin>} />
              <Route path="/usuarios/listaruser" element={<RequireAdmin><ListarUser /></RequireAdmin>} />
            </Routes>
          </main>
          <Footer />
        </div>
      </ModalProvider>
    </MessageProvider>
  );
}
