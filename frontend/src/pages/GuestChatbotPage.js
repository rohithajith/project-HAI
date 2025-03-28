import React, { useState, useEffect, useRef, useCallback } from 'react';
import './GuestChatbotPage.css';

const GuestChatbotPage = () => {
    const [messages, setMessages] = useState([{ sender: 'bot', text: 'Connecting...' }]);
    const [inputValue, setInputValue] = useState('');
    const chatboxRef = useRef(null);

    const addMessage = useCallback((text, sender) => {
        setMessages(prevMessages => [...prevMessages, { sender, text }]);
    }, []);

    useEffect(() => {
        addMessage('Connected to server.', 'bot');
    }, [addMessage]);

    // Scroll chatbox to bottom when messages change
    useEffect(() => {
        if (chatboxRef.current) {
            chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        const messageText = inputValue.trim();
        if (messageText) {
            addMessage(messageText, 'user');
            try {
                const response = await fetch('http://localhost:5001/api/send-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: messageText }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log("Response from backend:", data); // Debugging
                addMessage(data.response || JSON.stringify(data), 'bot'); // Display bot response
            } catch (error) {
                console.error('Error sending message:', error);
                console.error("Full error object:", error); // Debugging
                addMessage('Error sending message. Check console.', 'bot');
            }
            setInputValue('');
        }
    };

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="page-container chatbot-page">
            <h2>Guest Chatbot</h2>
            <div className="chatbox" ref={chatboxRef}>
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                />
                <button onClick={handleSend}>Send</button>
            </div>
        </div>
    );
};

export default GuestChatbotPage;