import React, { useState } from 'react';
import { Home, Workflow, History, Settings, Send, Bot, User, Clock, Coins, Activity } from 'lucide-react';
import './App.css';

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '¡Hola! Soy tu asistente de orquestación de flujos de trabajo. ¿En qué te puedo ayudar hoy?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [cost, setCost] = useState('0.000000');
  const [tokens, setTokens] = useState('0');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_data: input,
          session_id: 'session_test'
        })
      });

      if (!response.ok) throw new Error('Error de la conexión');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullResponseText = ''; 
      let hasAddedCost = false;   
      let hasAddedTokens = false; 

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunkValue = decoder.decode(value, { stream: true });
          fullResponseText += chunkValue;

          // 1. Extraer y SUMAR el coste al acumulado total (con validación)
          const costMatch = fullResponseText.match(/\[COST:\$([\d.]+)\]/);
          if (costMatch && !hasAddedCost) {
            const newCost = parseFloat(costMatch[1]) || 0;
            setCost(prev => {
              const current = parseFloat(prev) || 0;
              return (current + newCost).toFixed(6);
            });
            hasAddedCost = true; 
          }

          // 2. Extraer y SUMAR los tokens al acumulado total (con validación)
          const tokenMatch = fullResponseText.match(/\[TOKENS:(\d+)\]/);
          if (tokenMatch && !hasAddedTokens) {
            const newTokens = parseInt(tokenMatch[1], 10) || 0;
            setTokens(prev => {
              const current = parseInt(prev, 10) || 0;
              return (current + newTokens).toString();
            });
            hasAddedTokens = true;
          }

          // 3. Limpiar etiquetas del texto que ve el usuario
          const chatText = fullResponseText
            .replace(/\[COST:\$[\d.]+\]/g, '')
            .replace(/\[TOKENS:\d+\]/g, '')
            .trim();

          setMessages((prev) => {
            const updatedMessages = [...prev];
            const lastIndex = updatedMessages.length - 1;
            updatedMessages[lastIndex] = { ...updatedMessages[lastIndex], content: chatText };
            return updatedMessages;
          });
        }
      }
    } catch (error) {
      console.error('Error: ', error);
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Error: No se pudo conectar con el servidor' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="layout">
      <nav className="sidebar">
        <div className="sidebar-icon active" title="Home"><Home size={22} /></div>
        <div className="sidebar-icon" title="Workflows"><Workflow size={22} /></div>
        <div className="sidebar-icon" title="History"><History size={22} /></div>
        <div className="sidebar-icon settings-icon" title="Settings"><Settings size={22} /></div>
      </nav>

      <main className="main-chat">
        <header className="chat-header"><h1>Simple-Node Orchestrator</h1></header>
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">{msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}</div>
              <div className="message-content-wrapper">
                {msg.role === 'assistant' && <span className="ai-badge">ASSISTENT-PRO</span>}
                <div className="message-bubble">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar"><Bot size={18} /></div>
              <div className="message-content-wrapper">
                <span className="ai-badge">ASSISTENT-PRO</span>
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="chat-input-container">
          <form className="chat-form" onSubmit={handleSubmit}>
            <input 
              className="chat-input" 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              placeholder="Escribe un mensaje..." 
              disabled={isLoading} 
            />
            <button 
              type="submit" 
              className="send-button" 
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </main>

      <aside className="right-panel">
        <h2 className="panel-title">Node Stats</h2>
        <div className="stat-card">
          <div className="stat-icon"><Coins size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Coste Acumulado</span>
            <span className="stat-value">${cost}</span>
          </div>
        </div>
        <div className="stat-card" style={{ marginTop: '16px' }}>
          <div className="stat-icon"><Activity size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Tokens Totales</span>
            <span className="stat-value">{tokens}</span>
          </div>
        </div>
        <div className="stat-card" style={{ marginTop: '16px' }}>
          <div className="stat-icon"><Clock size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Tiempo de Ejecución</span>
            <span className="stat-value">1.2s</span>
          </div>
        </div>
      </aside>
    </div>
  );
}