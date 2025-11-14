import React, { createContext, useCallback, useState } from 'react';

export const MessageContext = createContext({ showMessage: () => {} });

export default function MessageProvider({ children }) {
  const [message, setMessage] = useState(null);
  const [visible, setVisible] = useState(false);

  const showMessage = useCallback((text, isError = false) => {
    setMessage({ text, isError });
    setVisible(true);
    setTimeout(() => setVisible(false), 5000);
  }, []);

  return (
    <MessageContext.Provider value={{ showMessage }}>
      {children}
      {visible && message && (
        <div
          className="msg"
          style={{
            position: 'fixed',
            top: 20,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 2000,
            padding: 12,
            borderRadius: 6,
            fontWeight: 'bold',
            textAlign: 'center',
            backgroundColor: message.isError ? '#f8d7da' : '#d1edff',
            color: message.isError ? '#721c24' : '#004085',
            border: '1px solid ' + (message.isError ? '#f5c6cb' : '#b8daff'),
            minWidth: 200,
          }}
        >
          {message.text}
        </div>
      )}
    </MessageContext.Provider>
  );
}
