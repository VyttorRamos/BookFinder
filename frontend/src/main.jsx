import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

import './assets/css/style.css';
import './assets/css/home.css';
import './assets/css/login.css';
import './assets/css/busca.css';
import './assets/css/text-pages.css';
import './assets/css/tabelas.css';
import './assets/css/generos.css';
import './assets/css/contato.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
