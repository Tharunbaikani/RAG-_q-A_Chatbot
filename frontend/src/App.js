



import React, { useState, useEffect } from "react";
import axios from "axios";
import { FaUser, FaRobot } from "react-icons/fa";
import "./App1.css";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  // Clear chat on refresh
  useEffect(() => {
    setChat([]); // Reset chat messages
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    await axios.post("http://127.0.0.1:8000/upload/", formData);
    setIsUploading(false);
    alert("File uploaded successfully!");
  };

  const handleSendMessage = async () => {
    if (!message) return;

    const formData = new FormData();
    formData.append("query", message);

    const response = await axios.post("http://127.0.0.1:8000/query/", formData);

    setChat([...chat, { user: message, bot: response.data.response }]);
    setMessage("");
  };

  return (
    <div className="chat-container">
      <h1 className="chat-title">🧠 AI Chatbot</h1>

      <div className="file-upload">
        <input type="file" id="file-input"onChange={handleFileChange} hidden />
        <label htmlFor="file-input" className="upload-btn">Choose File</label>
        
        {file && <span className="file-name">{file.name}</span>}
        <button onClick={handleUpload} className="upload-btn" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      <div className="chat-box">
        {chat.map((c, i) => (
          <div key={i}>
            {/* User Message (Right Side) */}
            <div className="message-wrapper user-wrapper">
              <div className="message-container user-message">
                <span className="user-icon"><FaUser /></span>
                <p><b>{c.user}</b></p>
              </div>
            </div>

            {/* Bot Message (Left Side) */}
            <div className="message-wrapper bot-wrapper">
              <div className="message-container bot-message">
                <span className="bot-icon"><FaRobot /></span>
                <p><b>{c.bot}</b></p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="input-box">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask anything from your Pdf..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;

