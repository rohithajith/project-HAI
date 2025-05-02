import React, { useEffect, useState } from "react";
import { Modal, Button, Badge, Form, Alert } from "react-bootstrap";
import { FaWrench, FaSpa, FaConciergeBell, FaRobot, FaExclamationTriangle } from "react-icons/fa";
import socket from "../socket";
import ChatBot from "../components/ChatBot";
import "animate.css";
import "./Dashboard.css";

const statusBadge = {
  Pending: "warning",
  "In Progress": "primary",
  Scheduled: "info",
  Completed: "success",
};

const typeIcons = {
  "Room Service": <FaConciergeBell className="text-info me-2" />,
  Maintenance: <FaWrench className="text-warning me-2" />,
  Wellness: <FaSpa className="text-danger me-2" />,
};

const Dashboard = () => {
  const [agent] = useState(localStorage.getItem("agent") || "Guest");
  const [requests, setRequests] = useState(() => {
    const saved = localStorage.getItem("dashboardRequests");
    return saved ? JSON.parse(saved) : [];
  });
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showCompletedOnly, setShowCompletedOnly] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isSosAlert, setIsSosAlert] = useState(false);
  const [sosRoom, setSosRoom] = useState(null);

  useEffect(() => {
    const handleRequest = (data) => {
      const id = `${data.timestamp}-${data.room}-${data.agent}`;
      setRequests((prev) => {
        const exists = prev.some(
          (r) => `${r.timestamp}-${r.room}-${r.agent}` === id
        );
        if (!exists) {
          const updated = [...prev, data];
          localStorage.setItem("dashboardRequests", JSON.stringify(updated));
          return updated;
        } else {
          return prev.map((r) =>
            `${r.timestamp}-${r.room}-${r.agent}` === id ? { ...r, ...data } : r
          );
        }
      });

      if (data.agent === "SOSAgent") {
        setSosRoom(data.room);
        setIsSosAlert(true);
        setTimeout(() => setIsSosAlert(false), 10000);
      }
    };

    const handleRating = ({ room, agent: ratedAgent, rating }) => {
      setRequests((prev) => {
        const updated = prev.map((req) =>
          req.room === room && req.agent === ratedAgent
            ? { ...req, rating }
            : req
        );
        localStorage.setItem("dashboardRequests", JSON.stringify(updated));
        return updated;
      });
    };

    socket.on("guest_response", handleRequest);
    socket.on("rating_feedback", handleRating);

    return () => {
      socket.off("guest_response", handleRequest);
      socket.off("rating_feedback", handleRating);
    };
  }, [agent]);

  const handleOpen = (room) => {
    setSelectedRoom(room);
    setShowModal(true);
  };

  const handleClose = () => {
    setSelectedRoom(null);
    setShowModal(false);
  };

  const handleStatusUpdate = (room, timestamp, agentId, requestData) => {
    const updated = requests.map((req) =>
      req.room === room && req.timestamp === timestamp && req.agent === agentId
        ? { ...req, status: "Completed" }
        : req
    );
    setRequests(updated);
    localStorage.setItem("dashboardRequests", JSON.stringify(updated));
    socket.emit("request_completed", { ...requestData, status: "Completed" });
  };

  const handleReset = () => {
    localStorage.removeItem("dashboardRequests");
    setRequests([]);
  };

  const getRatingBadge = (rating) => {
    if (!rating) return null;
    if (rating <= 2) return "danger";
    if (rating === 3) return "warning";
    return "success";
  };

  const filteredRequests = requests;
  const roomBased = filteredRequests.filter((r) => r.room);
  const miscBased = filteredRequests.filter((r) => !r.room);
  const rooms = [...new Set(roomBased.map((r) => r.room))];
  const getRoomRequests = (room) => roomBased.filter((r) => r.room === room);

  const isRoomCompleted = (room) => {
    const roomRequests = getRoomRequests(room);
    return roomRequests.every((r) => r.status === "Completed");
  };

  const displayedRooms = showCompletedOnly
    ? rooms.filter((room) => isRoomCompleted(room))
    : rooms;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2 className="animate__animated animate__fadeIn">
          {agent === "Admin" ? "🏨 Admin Dashboard" : `📬 ${agent} Dashboard`}
        </h2>
        <div className="d-flex gap-3 align-items-center">
          <Form.Check
            type="switch"
            label="Show Only Completed Rooms"
            checked={showCompletedOnly}
            onChange={(e) => setShowCompletedOnly(e.target.checked)}
          />
          <Button variant="outline-danger" onClick={handleReset}>
            🔁 Reset All
          </Button>
        </div>
      </div>

      {isSosAlert && (
        <Alert
          variant="danger"
          className="text-center animate__animated animate__flash animate__infinite infinite"
        >
          <FaExclamationTriangle className="me-2" /> 🚨 Emergency Request Received from Room #{sosRoom}!
        </Alert>
      )}

      {displayedRooms.length === 0 && miscBased.length === 0 && (
        <p className="text-muted text-center">No service requests yet.</p>
      )}

      <div className="row g-4">
        {displayedRooms.map((room) => (
          <div key={room} className="col-md-4">
            <div
              className={`card shadow border-start border-4 hover-shadow animate__animated animate__fadeInUp dashboard-room-card ${
                isRoomCompleted(room) ? "bg-light border-success" : "border-info"
              }`}
              onClick={() => handleOpen(room)}
              style={{ cursor: "pointer" }}
            >
              <div className="card-body text-center">
                <h5 className="card-title">
                  Room #{room}
                  {isRoomCompleted(room) && (
                    <Badge bg="success" className="ms-2">
                      ✅ All Done
                    </Badge>
                  )}
                </h5>
                <p className="text-muted mb-0">
                  {getRoomRequests(room).length} request(s)
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal show={showModal} onHide={handleClose} centered size="lg">
        <Modal.Header closeButton>
          <Modal.Title>📋 Requests for Room #{selectedRoom}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {getRoomRequests(selectedRoom).map((req, idx) => (
            <div key={idx} className="mb-4 border-bottom pb-3">
              <div className="d-flex justify-content-between align-items-center">
                <div className="fw-semibold">
                  {typeIcons[req.type]} {req.type}
                  <Badge bg="secondary" className="ms-2">Agent: {req.agent}</Badge>
                </div>
                <span className={`badge bg-${statusBadge[req.status] || "secondary"}`}>
                  {req.status || "Pending"}
                </span>
              </div>
              <div className="small text-muted">🕒 {req.time || "Just now"}</div>
              <div className="mb-2">
                <strong>🧾 Guest Request:</strong>
                <p className="mb-1">{req.original_request || "N/A"}</p>
              </div>
              <div className="mb-2">
                <strong>🤖 AI Response:</strong>
                <p className="mb-1">{req.response}</p>
              </div>
              {req.rating && (
                <div className="mt-2">
                  <span className={`badge bg-${getRatingBadge(req.rating)} px-2 py-1`}>
                    ⭐ {req.rating}/5
                  </span>
                </div>
              )}
              {req.status !== "Completed" && (
                <Button
                  size="sm"
                  variant="outline-success"
                  className="mt-2"
                  onClick={() => handleStatusUpdate(req.room, req.timestamp, req.agent, req)}
                >
                  Mark as Done
                </Button>
              )}
            </div>
          ))}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      <button className="chatbot-toggle-button" onClick={() => setShowChat(!showChat)}>
        <FaRobot />
      </button>

      {showChat && (
        <div className={`chatbot-popup ${agent !== "Guest" ? "chatbot-no-room" : ""}`}>
          <div className="chatbot-popup-header">
            Hotel Assistant
            <button
              onClick={() => setShowChat(false)}
              style={{ background: "transparent", border: "none", color: "#fff" }}
            >
              ✖
            </button>
          </div>
          <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
            <ChatBot role={agent} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;