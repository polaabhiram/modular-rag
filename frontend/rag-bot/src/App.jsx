import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);

  const sendMessage = () => {
    if (!input.trim() && !selectedFile) return;

    const userMessage = {
      role: "user",
      content: input,
      file: selectedFile,
    };

    const assistantMessage = {
      role: "assistant",
      content:
        "This is a sample response from the RAG system. [1] nova.txt",
    };

    setMessages([...messages, userMessage, assistantMessage]);

    setInput("");
    setSelectedFile(null);
  };

  const newChat = () => {
    setMessages([]);
    setInput("");
    setSelectedFile(null);
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      setSelectedFile(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
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
              <p>
                Ask a question or upload a document.
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <div className="message-label">
                {message.role === "user"
                  ? "You"
                  : "Assistant"}
              </div>

              {message.file && (
                <div className="message-file">
                  📄 {message.file.name}
                </div>
              )}

              {message.content && (
                <div className="message-content">
                  {message.content}
                </div>
              )}
            </div>
          ))}

        </div>

        {/* Input Area */}
        <div className="input-area">

          {/* Selected File */}
          {selectedFile && (
            <div className="selected-file">
              <span>
                📄 {selectedFile.name}
              </span>

              <button onClick={removeFile}>
                ✕
              </button>
            </div>
          )}

          <div className="input-row">

            {/* File Upload */}
            <label className="file-button">
              📎

              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
              />
            </label>

            {/* Text Input */}
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

            {/* Send */}
            <button
              className="send-button"
              onClick={sendMessage}
            >
              Send
            </button>

          </div>

        </div>

      </main>
    </div>
  );
}

export default App;