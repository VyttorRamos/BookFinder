import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import MessageProvider from './components/MessageProvider';
import ModalProvider from './components/ModalProvider';
import AdminSelects from './components/AdminSelects';
import CaptchaHandler from './components/CaptchaHandler';
import RequireAdmin from './components/RequireAdmin';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Landing from './pages/Landing';
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

// editoras - ADICIONE ESTES IMPORTS
import CadastrarEditora from './pages/editoras/CadastrarEditora';
import EditarEditora from './pages/editoras/EditarEditora';
import ExcluirEditora from './pages/editoras/ExcluirEditora';
import ListarEditoras from './pages/editoras/ListarEditoras';

// emprestimos - ADICIONE ESTES IMPORTS
import Devolver from './pages/emprestimos/Devolver';
import Emprestar from './pages/emprestimos/Emprestar';
import ListarAtrasados from './pages/emprestimos/ListarAtrasados';
import ListarEmprestimos from './pages/emprestimos/ListarEmprestimos';
import Renovar from './pages/emprestimos/Renovar';

// generos subpages - ADICIONE ESTES IMPORTS
import CadastrarGenero from './pages/generos/CadastrarGenero';
import EditarGenero from './pages/generos/EditarGenero';
import ExcluirGenero from './pages/generos/ExcluirGenero';
import ListarGeneros from './pages/generos/ListarGeneros';

// livros - ADICIONE ESTES IMPORTS
import CadastrarLivro from './pages/livros/CadastrarLivro';
import EditarLivro from './pages/livros/EditarLivro';
import ExcluirLivro from './pages/livros/ExcluirLivro';
import ListarLivro from './pages/livros/ListarLivro';

// multas - ADICIONE ESTES IMPORTS
import ListarMultas from './pages/multas/ListarMultas';
import RemoverMulta from './pages/multas/RemoverMulta';

// usuarios - ADICIONE ESTES IMPORTS
import EditarUser from './pages/usuarios/EditarUser';
import ExcluirUser from './pages/usuarios/ExcluirUser';
import ListarUser from './pages/usuarios/ListarUser';

// Componente para rotas protegidas
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Componente para rotas públicas (quando já está autenticado)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return !isAuthenticated ? children : <Navigate to="/home" />;
};

export default function App() {
  return (
    <AuthProvider>
      <MessageProvider>
        <ModalProvider>
          <div className="app-root">
            <AdminSelects />
            <CaptchaHandler />
            <Header />
            <main>
              <Routes>
                {/* Rota raiz - redireciona baseado na autenticação */}
                <Route path="/" element={<Navigate to="/landing" replace />} />
                
                {/* Landing Page (apenas para não autenticados) */}
                <Route 
                  path="/landing" 
                  element={
                    <PublicRoute>
                      <Landing />
                    </PublicRoute>
                  } 
                />
                
                {/* Home (apenas para autenticados) */}
                <Route 
                  path="/home" 
                  element={
                    <ProtectedRoute>
                      <Home />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Login e Register (apenas para não autenticados) */}
                <Route 
                  path="/login" 
                  element={
                    <PublicRoute>
                      <Login />
                    </PublicRoute>
                  } 
                />
                <Route 
                  path="/register" 
                  element={
                    <PublicRoute>
                      <Register />
                    </PublicRoute>
                  } 
                />
                
                {/* Rotas públicas acessíveis a todos */}
                <Route path="/busca" element={<Search />} />
                <Route path="/buscar_livros" element={<BuscarLivros />} />
                <Route path="/contato" element={<Contato />} />
                <Route path="/sobre" element={<Sobre />} />
                <Route path="/privacidade" element={<Privacidade />} />
                <Route path="/termos" element={<Termos />} />
                <Route path="/error" element={<ErrorPage />} />
                
                {/* Dashboard e rotas administrativas (protegidas + admin) */}
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <Dashboard />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                
                <Route 
                  path="/generos" 
                  element={
                    <ProtectedRoute>
                      <GenerosPage />
                    </ProtectedRoute>
                  } 
                />

                {/* Rotas administrativas (protegidas + admin) */}
                
                {/* EDITORAS */}
                <Route 
                  path="/editoras/cadastrareditora" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <CadastrarEditora />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/editoras/editareditora" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <EditarEditora />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/editoras/excluireditora" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ExcluirEditora />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/editoras/listareditoras" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarEditoras />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* EMPRÉSTIMOS */}
                <Route 
                  path="/emprestimos/devolver" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <Devolver />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/emprestimos/emprestar" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <Emprestar />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/emprestimos/listaratrasados" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarAtrasados />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/emprestimos/listaremprestimos" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarEmprestimos />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/emprestimos/renovar" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <Renovar />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* GÊNEROS */}
                <Route 
                  path="/generos/cadastrargenero" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <CadastrarGenero />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/generos/editargenero" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <EditarGenero />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/generos/excluirgenero" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ExcluirGenero />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/generos/listargeneros" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarGeneros />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* LIVROS */}
                <Route 
                  path="/livros/cadastrarlivro" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <CadastrarLivro />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/livros/editarlivro/:id" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <EditarLivro />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/livros/excluirlivro/:id" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ExcluirLivro />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/livros/listarlivro" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarLivro />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* MULTAS */}
                <Route 
                  path="/multas/listarmultas" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarMultas />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/multas/removermulta" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <RemoverMulta />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* USUÁRIOS */}
                <Route 
                  path="/usuarios/editaruser" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <EditarUser />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/usuarios/excluiruser" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ExcluirUser />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/usuarios/listaruser" 
                  element={
                    <ProtectedRoute>
                      <RequireAdmin>
                        <ListarUser />
                      </RequireAdmin>
                    </ProtectedRoute>
                  } 
                />

                {/* Rota fallback */}
                <Route path="*" element={<ErrorPage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </ModalProvider>
      </MessageProvider>
    </AuthProvider>
  );
}