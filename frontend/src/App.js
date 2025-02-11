



import React, { useState, useEffect } from "react";
import axios from "axios";
import { FaUser, FaRobot } from "react-icons/fa";
import "./App1.css";

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false); // Track PDF upload status-R
  const [isTyping, setIsTyping] = useState(false); // :NEW: Track bot typing effect
  const [typingInterval, setTypingInterval] = useState(null);

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

    try {
      await axios.post("http://127.0.0.1:8000/upload/", formData);
      setIsUploaded(true); // Mark upload as complete
      alert("File uploaded successfully!");
    } catch (error) {
      alert("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };


  
  

  const handleSendMessage = async () => {
    if (!message) return;

    setChat([...chat, { user: message, bot: "Typing..." }]); // :NEW: Show "Typing..." first
    setIsTyping(true); // :NEW: Disable send button while bot is typing


    const formData = new FormData();
    formData.append("query", message);

    const response = await axios.post("http://127.0.0.1:8000/query/", formData);

    // setChat([...chat, { user: message, bot: response.data.response }]);
    simulateTypingEffect(response.data.response); // :NEW: Call typewriter effect
    setMessage("");
  };
  //new func
  
  const handleStopTyping = () => {
    if (typingInterval) {
      clearInterval(typingInterval);
      setTypingInterval(null);
      setIsTyping(false);
    }
  };



  // :NEW: Function to simulate typewriter effect
  const simulateTypingEffect = (fullText) => {
    let index = 0;
  
    setTimeout(() => {
      setChat((prevChat) => {
        const newChat = [...prevChat];
        newChat[newChat.length - 1].bot = ""; // Clear "Typing..."
        return newChat;
      });
  
      const interval = setInterval(() => {
        setChat((prevChat) => {
          const newChat = [...prevChat];
          if (index < fullText.length) {
            newChat[newChat.length - 1].bot = fullText.slice(0, index + 1); // Append correctly
          }
          return newChat;
        });
  
        index++;
        if (index === fullText.length) {
          clearInterval(interval);
          setIsTyping(false); // Re-enable send button after typing is done
        }
      }, 20);
      setTypingInterval(interval); // Adjust typing speed here
    }, 300);
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
          // placeholder="Ask anything from your Pdf..."
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault(); // Prevents form submission (if any)
              handleSendMessage(); // Calls the send function
            }
          }}
          placeholder={isUploaded ? "Ask anything from your PDF..." : "Upload a PDF first!"}
          disabled={!isUploaded || isTyping} // :NEW: Disable input if typing
          // disabled={!isUploaded} // Disable input if PDF is not uploaded
        />
        {/* <button onClick={handleSendMessage}>Send</button> */}

        

        <button onClick={isTyping ? handleStopTyping : handleSendMessage}>
          {isTyping ? "Stop" : "Send"}
        </button>



      </div>
    </div>
  );
}

export default App;

