import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function AdminSelects() {
  const navigate = useNavigate();

  useEffect(() => {
    function init() {
      const selects = document.querySelectorAll('.admin-select');
      selects.forEach(select => {
        function onChange(e) {
          const url = (e.target && e.target.value) ? e.target.value.trim() : '';
          if (!url) return;
          // Use SPA navigation
          navigate(url);
        }
        select.addEventListener('change', onChange);
        // store listener reference for cleanup
        select.__bf_onchange = onChange;
      });
    }

    init();

    return () => {
      const selects = document.querySelectorAll('.admin-select');
      selects.forEach(select => {
        if (select.__bf_onchange) select.removeEventListener('change', select.__bf_onchange);
      });
    };
  }, [navigate]);

  return null;
}
