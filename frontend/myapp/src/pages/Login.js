import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "animate.css";

const dummyUsers = {
  "guest@hotel.com": { password: "Guest123!", role: "Guest" },
  "admin@hotel.com": { password: "Admin123!", role: "Admin" },
  "maintenance@hotel.com": { password: "Agent123!", role: "MaintenanceAgentAgent" },
  "manager@hotel.com": { password: "Manager123!", role: "Manager" },
  "roomservice@hotel.com": { password: "Agent123!", role: "RoomServiceAgentAgent" },
  "wellness@hotel.com": { password: "Agent123!", role: "WellnessAgentAgent" },
};

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    const user = dummyUsers[email];
    if (user && user.password === password) {
      localStorage.setItem("agent", user.role);
      if (user.role === "Guest") {
        localStorage.removeItem("roomNumber");
      }
      navigate("/dashboard");
    } else {
      setError("Invalid credentials. Please try again.");
    }
  };

  return (
    <div className="d-flex align-items-center justify-content-center vh-100 bg-dark text-light animate__animated animate__fadeIn">
      <div className="p-4 bg-white rounded-4 shadow-lg text-dark" style={{ minWidth: "350px" }}>
        <h4 className="mb-4 text-center text-primary">🔐 Hotel AI Login</h4>
        <input
          type="email"
          className="form-control mb-3"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          className="form-control mb-3"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <div className="text-danger small mb-2">{error}</div>}
        <button className="btn btn-primary w-100" onClick={handleLogin}>
          Login
        </button>
      </div>
    </div>
  );
}
