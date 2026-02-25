import { useState } from 'react'
import './App.css'

function App() {

  const [messages, setMessages] = useState([ { role: 'assistant', content: ' Hola, soy tu asistente en que te puedo ayudar?'}]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault();
    const newMessage = {role: 'user', content: input};
    setMessages(prevMessages => [...prevMessages, newMessage])
    setInput('')

  }

  return (
    <div id='Principal'>
      <div id='Historial'>
        {messages.map((msg, index) => (
          <div key={index}>
            <strong>{msg.role === 'user' ? 'Tú' : 'Asistente'}:</strong>{msg.content}
          </div>
        ))}
        <form onSubmit={handleSubmit}>
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)}/>
          <button type='submit' disabled={isLoading}>
            {isLoading ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </div>
    </div>
  )
  }

export default App
