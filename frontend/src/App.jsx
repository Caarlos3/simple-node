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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Añadir el mensaje del usuario al estado
    setMessages((prev) => [...prev, { role: 'user', content: input }]);

    // Limpiar el input
    setInput('');

    setIsLoading(true);

    // TODO: Implementar streaming con el mentor aquí.

    // Simulación temporal para quitar el estado de carga (se removerá al implementar streaming)
    setTimeout(() => setIsLoading(false), 500);
  };

  return (
    <div className="layout">
      {/* SIDEBAR IZQUIERDO */}
      <nav className="sidebar">
        <div className="sidebar-icon active" title="Home">
          <Home size={22} strokeWidth={2} />
        </div>
        <div className="sidebar-icon" title="Workflows">
          <Workflow size={22} strokeWidth={2} />
        </div>
        <div className="sidebar-icon" title="History">
          <History size={22} strokeWidth={2} />
        </div>
        <div className="sidebar-icon settings-icon" title="Settings">
          <Settings size={22} strokeWidth={2} />
        </div>
      </nav>

      {/* ÁREA CENTRAL - CHAT */}
      <main className="main-chat">
        <header className="chat-header">
          <h1>Workflow Orchestrator</h1>
        </header>

        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>
              <div className="message-content-wrapper">
                {msg.role === 'assistant' && (
                  <span className="ai-badge">LLM-NODE-01</span>
                )}
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={18} />
              </div>
              <div className="message-content-wrapper">
                <span className="ai-badge">LLM-NODE-01</span>
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
              type="text"
              className="chat-input"
              placeholder="Escribe un prompt para ajustar el flujo de trabajo..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isLoading || !input.trim()}
            >
              <Send size={18} strokeWidth={2.5} />
            </button>
          </form>
        </div>
      </main>

      {/* PANEL DERECHO - METADATOS */}
      <aside className="right-panel">
        <div>
          <h2 className="panel-title">Node Stats</h2>

          <div className="stat-card">
            <div className="stat-icon">
              <Coins size={20} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Coste Estimado</span>
              <span className="stat-value">$0.0042</span>
            </div>
          </div>

          <div className="stat-card" style={{ marginTop: '16px' }}>
            <div className="stat-icon">
              <Activity size={20} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Tokens Totales</span>
              <span className="stat-value">1,248</span>
            </div>
          </div>

          <div className="stat-card" style={{ marginTop: '16px' }}>
            <div className="stat-icon">
              <Clock size={20} />
            </div>
            <div className="stat-info">
              <span className="stat-label">Tiempo de Ejecución</span>
              <span className="stat-value">1.2s</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
