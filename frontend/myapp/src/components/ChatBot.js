import React, { useEffect, useState } from "react";
import socket from "../socket";
import { FaStar } from "react-icons/fa";

const ChatBot = () => {
  const [roomNumber, setRoomNumber] = useState("");
  const [confirmedRoom, setConfirmedRoom] = useState(localStorage.getItem("roomNumber") || "");
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [status, setStatus] = useState("🔴 Disconnected");
  const [awaitingRating, setAwaitingRating] = useState(null);
  const [ratingGiven, setRatingGiven] = useState(null);

  const extractAssistantReply = (rawText) => {
    return rawText.includes("<|assistant|>")
      ? rawText.split("<|assistant|>").pop().trim()
      : rawText.trim();
  };

  useEffect(() => {
    socket.on("connect", () => setStatus("🟢 Connected"));
    socket.on("disconnect", () => setStatus("🔴 Disconnected"));

    socket.on("guest_response", (data) => {
      const cleaned = extractAssistantReply(data.response);
      setChatLog((prev) => [...prev, { role: "AI", content: cleaned, agent: data.agent }]);

      if (data.status === "Completed") {
        setAwaitingRating({ room: data.room, agent: data.agent });
        setRatingGiven(null);
      }
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("guest_response");
    };
  }, []);

  const sendMessage = () => {
    if (message.trim() && confirmedRoom) {
      socket.emit("guest_message", { content: message, room: confirmedRoom });
      setChatLog((prev) => [...prev, { role: "You", content: message }]);
      setMessage("");
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

      setChatLog((prev) => [
        ...prev,
        { role: "You", content: `⭐ I rate the service ${rating}/5 - ${label}` },
        { role: "AI", content: `🙏 Thank you for rating us ${rating}/5 (${label})!` },
      ]);

      setRatingGiven(rating);
      setAwaitingRating(null);
    }
  };

  const getRatingColor = (rating) => {
    if (rating <= 2) return "#dc3545"; // red
    if (rating === 3) return "#fd7e14"; // orange
    return "#28a745"; // green
  };

  if (!confirmedRoom) {
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
            if (roomNumber.trim()) {
              localStorage.setItem("roomNumber", roomNumber.trim());
              setConfirmedRoom(roomNumber.trim());
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
        <br />
        <small className="text-muted">Room #{confirmedRoom}</small>
      </h4>

      <div className="border rounded p-3 mb-3 bg-light" style={{ height: "250px", overflowY: "auto" }}>
        {chatLog.map((msg, idx) => (
          <p key={idx} className={`mb-2 ${msg.role === "You" ? "text-end" : "text-start"}`}>
            <strong>{msg.role}:</strong> {msg.content}
            {msg.agent && msg.role === "AI" && (
              <span className="badge bg-secondary ms-2">{msg.agent}</span>
            )}
          </p>
        ))}
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
                    color: ratingGiven && ratingGiven >= star ? getRatingColor(ratingGiven) : "#ffc107",
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
        <button className="btn btn-primary" onClick={sendMessage}>Send</button>
      </div>

      <button
        onClick={() => {
          localStorage.removeItem("agent");
          localStorage.removeItem("roomNumber");
          window.location.reload();
        }}
        style={{
          position: "fixed",
          top: 10,
          right: 10,
          padding: "8px 12px",
          backgroundColor: "#dc3545",
          color: "white",
          border: "none",
          borderRadius: "5px",
          zIndex: 1000,
        }}
      >
        Reset Role
      </button>
    </div>
  );
};

export default ChatBot;
