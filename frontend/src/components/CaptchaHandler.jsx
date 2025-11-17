import { useContext, useEffect } from 'react';
import { MessageContext } from './MessageProvider';

export default function CaptchaHandler() {
  const { showMessage } = useContext(MessageContext);

  useEffect(() => {
    // Attach CAPTCHA validation to any form that has #notrobo
    function attachCaptcha() {
      const forms = Array.from(document.querySelectorAll('form'));
      forms.forEach(form => {
        const captchaInput = form.querySelector('#notrobo');
        if (!captchaInput) return;

        function onSubmit(e) {
          const val = (captchaInput.value || '').trim();
          if (!val) {
            e.preventDefault();
            showMessage('Por favor, responda a pergunta do CAPTCHA.', true);
            captchaInput.focus();
            return false;
          }
          if (!/^\d+$/.test(val)) {
            e.preventDefault();
            showMessage('A resposta deve conter apenas números.', true);
            captchaInput.focus();
            return false;
          }
        }

        if (!form.__bf_captcha_attached) {
          form.addEventListener('submit', onSubmit);
          form.__bf_captcha_attached = onSubmit;
        }
      });
    }

    // Attach search form redirect (id=search-form)
    function attachSearch() {
      const searchForm = document.getElementById('search-form');
      if (!searchForm) return;

      function onSearch(e) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        const term = searchInput ? (searchInput.value || '').trim() : '';
        if (!term) return;
        window.location.href = `/busca?q=${encodeURIComponent(term)}`;
      }

      if (!searchForm.__bf_search_attached) {
        searchForm.addEventListener('submit', onSearch);
        searchForm.__bf_search_attached = onSearch;
      }
    }

    // Fade-in on scroll
    function configureFadeIn() {
      const elements = Array.from(document.querySelectorAll('.fade-in'));
      function check() {
        const windowHeight = window.innerHeight;
        elements.forEach(el => {
          const rect = el.getBoundingClientRect();
          if (rect.top < windowHeight - 100) el.classList.add('visible');
        });
      }
      check();
      window.addEventListener('scroll', check);
      return () => window.removeEventListener('scroll', check);
    }

    // Navbar scroll effect
    function configureNavbarScroll() {
      function onScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        if (window.scrollY > 50) navbar.classList.add('scrolled');
        else navbar.classList.remove('scrolled');
      }
      onScroll();
      window.addEventListener('scroll', onScroll);
      return () => window.removeEventListener('scroll', onScroll);
    }

    // Smooth anchor links
    function attachSmoothAnchors() {
      const anchors = Array.from(document.querySelectorAll('a[href^="#"]'));
      anchors.forEach(a => {
        function onClick(e) {
          const href = a.getAttribute('href');
          if (!href || href === '#') return;
          e.preventDefault();
          const target = document.querySelector(href);
          if (!target) return;
          window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });
          // close mobile menu if open
          const mobileMenu = document.querySelector('.menu.mobile-open');
          if (mobileMenu) mobileMenu.classList.remove('mobile-open');
        }
        if (!a.__bf_anchor_attached) {
          a.addEventListener('click', onClick);
          a.__bf_anchor_attached = onClick;
        }
      });

      return () => {
        anchors.forEach(a => {
          if (a.__bf_anchor_attached) {
            a.removeEventListener('click', a.__bf_anchor_attached);
            delete a.__bf_anchor_attached;
          }
        });
      };
    }

    attachCaptcha();
    attachSearch();
    const cleanupFade = configureFadeIn();
    const cleanupNavbar = configureNavbarScroll();
    const cleanupAnchors = attachSmoothAnchors();

    const mo = new MutationObserver(() => {
      attachCaptcha();
      attachSearch();
    });
    mo.observe(document.body, { childList: true, subtree: true });

    return () => {
      // remove attached listeners
      const forms = Array.from(document.querySelectorAll('form'));
      forms.forEach(form => {
        if (form.__bf_captcha_attached) {
          form.removeEventListener('submit', form.__bf_captcha_attached);
          delete form.__bf_captcha_attached;
        }
        if (form.__bf_search_attached) {
          form.removeEventListener('submit', form.__bf_search_attached);
          delete form.__bf_search_attached;
        }
      });
      cleanupFade();
      cleanupNavbar();
      cleanupAnchors();
      mo.disconnect();
    };
  }, [showMessage]);

  return null;
}
