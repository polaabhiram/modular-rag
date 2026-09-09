import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    const assistantMessage = {
      role: "assistant",
      content:
        "This is a sample response from the RAG system. [1] nova.txt",
    };

    setMessages([...messages, userMessage, assistantMessage]);
    setInput("");
  };

  const newChat = () => {
    setMessages([]);
    setInput("");
  };

  return (
    <div className="app">

      {/* Sidebar */}
      <aside className="sidebar">
        <h2>RAG Chat</h2>

        <button onClick={newChat} className="new-chat">
          + New Chat
        </button>

        <div className="chat-list">
          <p>Today</p>

          <button className="chat-item">
            What is NovaDesk?
          </button>

          <button className="chat-item">
            Pricing information
          </button>

          <button className="chat-item">
            Customer support
          </button>
        </div>
      </aside>

      {/* Main Chat */}
      <main className="chat-container">

        <header className="chat-header">
          <h1>NovaDesk RAG</h1>
          <p>Ask questions about your documents</p>
        </header>

        {/* Messages */}
        <div className="messages">

          {messages.length === 0 && (
            <div className="welcome">
              <h2>How can I help?</h2>
              <p>Ask a question about your documents.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-label">
                {message.role === "user" ? "You" : "Assistant"}
              </div>

              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))}

        </div>

        {/* Input */}
        <div className="input-area">

          <input
            type="text"
            placeholder="Ask a question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
          />

          <button onClick={sendMessage}>
            Send
          </button>

        </div>

      </main>
    </div>
  );
}

export default App;