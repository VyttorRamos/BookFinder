import { useContext, useEffect } from 'react';
import { MessageContext } from './MessageProvider';

export default function CaptchaHandler() {
  const { showMessage } = useContext(MessageContext);

  useEffect(() => {
    function attach() {
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

        // attach if not already attached
        if (!form.__bf_captcha_attached) {
          form.addEventListener('submit', onSubmit);
          form.__bf_captcha_attached = onSubmit;
        }
      });
    }

    attach();

    // try again after navigation or dynamic changes
    const mo = new MutationObserver(() => attach());
    mo.observe(document.body, { childList: true, subtree: true });

    return () => {
      const forms = Array.from(document.querySelectorAll('form'));
      forms.forEach(form => {
        if (form.__bf_captcha_attached) {
          form.removeEventListener('submit', form.__bf_captcha_attached);
          delete form.__bf_captcha_attached;
        }
      });
      mo.disconnect();
    };
  }, [showMessage]);

  return null;
}
