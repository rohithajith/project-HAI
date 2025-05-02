import React, { useEffect, useState, useRef } from "react";
import socket from "../socket";
import { FaStar } from "react-icons/fa";

const ChatBot = ({ role }) => {
  const user = JSON.parse(localStorage.getItem("user")) || {};
  const isGuest = user.role === "Guest";
  const consent = user.consent === true;

  const [roomNumber, setRoomNumber] = useState(() => localStorage.getItem("roomNumber") || "");
  const [confirmedRoom, setConfirmedRoom] = useState(() => {
    return isGuest ? localStorage.getItem("roomNumber") || "" : user.role;
  });

  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const chatRef = useRef(null);
  const [status, setStatus] = useState("🔴 Disconnected");
  const [awaitingRating, setAwaitingRating] = useState(null);
  const [ratingGiven, setRatingGiven] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  const saveChat = (updatedLog) => {
    if (isGuest && confirmedRoom && consent) {
      localStorage.setItem(`chat_${confirmedRoom}`, JSON.stringify(updatedLog));
    }
  };

  useEffect(() => {
    if (isGuest && consent && confirmedRoom) {
      const roomChat = JSON.parse(localStorage.getItem(`chat_${confirmedRoom}`)) || [];
      setChatLog(roomChat);
    }
  }, [confirmedRoom]);

  useEffect(() => {
    const handleConnect = () => setStatus("🟢 Connected");
    const handleDisconnect = () => setStatus("🔴 Disconnected");
    const handleResponse = (data) => {
      const cleaned = data.response?.replace("<|assistant|>", "").trim();
      setIsTyping(false);

      if (data.room === confirmedRoom) {
        const updatedLog = [...chatLog, { role: "AI", content: cleaned, agent: data.agent }];
        setChatLog(updatedLog);
        saveChat(updatedLog);

        if (data.status === "Completed") {
          setAwaitingRating({ room: data.room, agent: data.agent });
          setRatingGiven(null);
        }
      }
    };

    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);
    socket.on("guest_response", handleResponse);

    if (socket.connected) {
      setStatus("🟢 Connected");
      if (chatLog.length === 0) {
        const initialMessage = [
          {
            role: "AI",
            content: "👋 Welcome to HOTEL AI! How may I help you today?",
          },
        ];
        setChatLog(initialMessage);
        saveChat(initialMessage);
      }
    }

    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("guest_response", handleResponse);
    };
  }, [confirmedRoom, chatLog]);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chatLog, isTyping]);

  const sendMessage = () => {
    if (message.trim() && confirmedRoom) {
      const updatedLog = [...chatLog, { role: "You", content: message }];
      setChatLog(updatedLog);
      saveChat(updatedLog);
      socket.emit("guest_message", { content: message, room: confirmedRoom });
      setMessage("");
      setIsTyping(true);
    }
  };

  const handleRating = (rating) => {
    if (awaitingRating) {
      socket.emit("rating_feedback", {
        rating,
        room: awaitingRating.room,
        agent: awaitingRating.agent,
      });

      const label = rating <= 2 ? "Poor" : rating === 3 ? "Average" : "Excellent";
      const updatedLog = [
        ...chatLog,
        { role: "You", content: `⭐ I rate the service ${rating}/5 - ${label}` },
        { role: "AI", content: `🙏 Thank you for rating us ${rating}/5 (${label})!` },
      ];

      setChatLog(updatedLog);
      saveChat(updatedLog);
      setRatingGiven(rating);
      setAwaitingRating(null);
    }
  };

  const getRatingColor = (rating) => {
    if (rating <= 2) return "#dc3545";
    if (rating === 3) return "#fd7e14";
    return "#28a745";
  };

  if (isGuest && !confirmedRoom.trim()) {
    return (
      <div className="p-4 mx-auto" style={{ maxWidth: "500px" }}>
        <h5 className="text-center mb-3">🏨 Enter Your Room Number</h5>
        <input
          type="text"
          className="form-control mb-3"
          placeholder="Room Number (e.g., 101)"
          value={roomNumber}
          onChange={(e) => setRoomNumber(e.target.value)}
        />
        <button
          className="btn btn-success w-100"
          onClick={() => {
            const trimmed = roomNumber.trim();
            if (trimmed) {
              localStorage.setItem("roomNumber", trimmed);
              setConfirmedRoom(trimmed);
              if (consent) {
                localStorage.setItem(`chat_${trimmed}`, JSON.stringify([]));
              }
              setChatLog([]);
            }
          }}
        >
          Proceed
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 mx-auto" style={{ maxWidth: "600px" }}>
      <h4 className="text-center mb-3">
        🧠 Hotel AI Chatbot {status}
        {confirmedRoom && (
          <>
            <br />
            <small className="text-muted"> #{confirmedRoom}</small>
          </>
        )}
      </h4>

      {!consent && (
        <div className="alert alert-warning text-center p-2 mb-3">
          ⚠️ You skipped giving consent. Your messages will not be saved and history will be lost when you close the app.
        </div>
      )}

      <div
        ref={chatRef}
        className="border rounded p-3 mb-3 bg-light"
        style={{ height: "250px", overflowY: "auto" }}
      >
        {chatLog.map((msg, idx) => (
          <p key={idx} className={`mb-2 ${msg.role === "You" ? "text-end" : "text-start"}`}>
            <strong>{msg.role}:</strong> {msg.content}
            {msg.agent && msg.role === "AI" && (
              <span className="badge bg-secondary ms-2">{msg.agent}</span>
            )}
          </p>
        ))}
        {isTyping && (
          <div className="text-start text-muted">
            <em>Hotel AI is typing...</em>
          </div>
        )}
        {awaitingRating && (
          <div className="text-center mt-3">
            <strong>🌟 How would you rate the service?</strong>
            <div className="d-flex justify-content-center mt-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <FaStar
                  key={star}
                  size={30}
                  style={{
                    cursor: "pointer",
                    marginRight: "5px",
                    color:
                      ratingGiven && ratingGiven >= star
                        ? getRatingColor(ratingGiven)
                        : "#ffc107",
                  }}
                  onClick={() => handleRating(star)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="d-flex">
        <input
          className="form-control me-2"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your message..."
        />
        <button className="btn btn-primary" onClick={sendMessage} disabled={!message.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;