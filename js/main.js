// Função para gerar o cabeçalho (barra de navegação)
function carregarHeader() {
    const headerContainer = document.createElement('header');
    
    // Identifica qual página está ativa para destacar o link no menu
    const paginaAtual = window.location.pathname.split('/').pop();

    headerContainer.innerHTML = `
        <nav>
            <div class="logo">
                <a href="index.html" title="BookFinder">
                    <img src="img/BookFinderIcon.png" alt="Logo BookFinder" />
                </a>
            </div>
            <ul class="menu">
                <li><a href="index.html#destaques" class="${paginaAtual.includes('index') || paginaAtual === '' ? 'active' : ''}">Recomendações</a></li>
                <li><a href="generos.html" class="${paginaAtual === 'generos.html' ? 'active' : ''}">Gêneros</a></li>
                <li><a href="sobre.html" class="${paginaAtual === 'sobre.html' ? 'active' : ''}">Sobre</a></li>
                <li><a href="contato.html" class="${paginaAtual === 'contato.html' ? 'active' : ''}">Contato</a></li>
            </ul>
        </nav>
    `;

    // Adiciona o cabeçalho ao corpo do documento
    document.body.prepend(headerContainer);
}

// Função para gerar o rodapé
function carregarFooter() {
    const footerContainer = document.createElement('footer');

    footerContainer.innerHTML = `
        <div class="footer-content">
            <p>&copy; ${new Date().getFullYear()} BookFinder. Todos os direitos reservados.</p>
            <p>Sua biblioteca acadêmica para encontrar as melhores leituras.</p>
            <ul class="footer-links">
                <li><a href="termos.html">Termos de Serviço</a></li>
                <li><a href="privacidade.html">Política de Privacidade</a></li>
                <li><a href="contato.html">Fale Conosco</a></li>
            </ul>
        </div>
    `;

    // Adiciona o rodapé ao final do corpo do documento
    document.body.appendChild(footerContainer);
}

// Chama as funções para carregar o cabeçalho e o rodapé quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    carregarHeader();
    carregarFooter();
});