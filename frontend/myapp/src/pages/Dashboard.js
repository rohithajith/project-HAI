import React, { useEffect, useState } from "react";
import { Modal, Button } from "react-bootstrap";
import { FaWrench, FaSpa, FaConciergeBell } from "react-icons/fa";
import socket from "../socket";
import "animate.css";

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

const Dashboard = ({ agent }) => {
  const [requests, setRequests] = useState(() => {
    const saved = localStorage.getItem("dashboardRequests");
    return saved ? JSON.parse(saved) : [];
  });

  const [selectedRoom, setSelectedRoom] = useState(null);
  const [showModal, setShowModal] = useState(false);

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
        }
        return prev;
      });
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
  }, []);

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
  
    // ✅ Emit to backend that this request is completed (for rating trigger)
    socket.emit("request_completed", {
      ...requestData,
      status: "Completed"
    });
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

  const filteredRequests =
    agent === "Admin" ? requests : requests.filter((r) => r.agent === agent);

  const rooms = [...new Set(filteredRequests.map((r) => r.room))];
  const getRoomRequests = (room) =>
    filteredRequests.filter((r) => r.room === room);

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 className="text-primary animate__animated animate__fadeIn">
          {agent === "Admin"
            ? "🏨 Admin Dashboard"
            : `🛎️ ${agent} Dashboard`}
        </h2>
        <Button variant="outline-danger" onClick={handleReset}>
          🔁 Reset All
        </Button>
      </div>

      {rooms.length === 0 && (
        <p className="text-muted text-center">No service requests yet.</p>
      )}

      <div className="row g-4">
        {rooms.map((room) => (
          <div key={room} className="col-md-4">
            <div
              className="card shadow border-start border-4 border-info hover-shadow animate__animated animate__fadeInUp"
              onClick={() => handleOpen(room)}
              style={{ cursor: "pointer" }}
            >
              <div className="card-body text-center">
                <h5 className="card-title">Room #{room}</h5>
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
                </div>
                <span
                  className={`badge bg-${statusBadge[req.status] || "secondary"}`}
                >
                  {req.status || "Pending"}
                </span>
              </div>
              <div className="small text-muted">🕒 {req.time || "Just now"}</div>
              <p className="mb-1">{req.response}</p>

              {req.rating && (
                <div className="mt-2">
                  <span
                    className={`badge bg-${getRatingBadge(req.rating)} px-2 py-1`}
                  >
                    ⭐ {req.rating}/5
                  </span>
                </div>
              )}

              {req.status !== "Completed" && (
                <Button
                  size="sm"
                  variant="outline-success"
                  className="mt-2"
                  onClick={() =>
                    handleStatusUpdate(req.room, req.timestamp, req.agent, req)
                  }                  
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
    </div>
  );
};

export default Dashboard;
