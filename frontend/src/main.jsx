import React from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';

import './assets/css/style.css';
import './assets/css/home.css';
import './assets/css/login.css';
import './assets/css/busca.css';
import './assets/css/text-pages.css';
import './assets/css/tabelas.css';
import './assets/css/generos.css';
import './assets/css/contato.css';

const router = createBrowserRouter([
  { path: '/*', element: <App /> }
], {
  future: { v7_startTransition: true }
});

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
