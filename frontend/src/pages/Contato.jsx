import React, { useState, useContext } from 'react';
import { MessageContext } from '../components/MessageProvider';

export default function Contato(){
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const { showMessage } = useContext(MessageContext);

  function handleSubmit(e){
    e.preventDefault();
    // No backend endpoint for contact, so just show a message for now
    showMessage('Mensagem enviada! Entraremos em contato em breve.');
    setName(''); setEmail(''); setSubject(''); setMessage('');
  }

  return (
    <div className="contact-container container">
      <h1>Fale Conosco</h1>
      <p>Tem alguma dúvida, sugestão ou crítica? Preencha o formulário abaixo ou entre em contato por um de nossos canais.</p>

      <form onSubmit={handleSubmit} className="contact-form">
        <div className="form-group">
          <label htmlFor="name">Nome</label>
          <input id="name" value={name} onChange={(e)=>setName(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="subject">Assunto</label>
          <input id="subject" value={subject} onChange={(e)=>setSubject(e.target.value)} required />
        </div>
        <div className="form-group">
          <label htmlFor="message">Mensagem</label>
          <textarea id="message" rows={6} value={message} onChange={(e)=>setMessage(e.target.value)} required />
        </div>
        <button type="submit" className="btn-primary">Enviar Mensagem</button>
      </form>
    </div>
  );
}
