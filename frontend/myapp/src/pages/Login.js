import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Modal, Button } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "animate.css";

const dummyUsers = {
  "guest@hotel.com": { password: "Guest123!", role: "Guest" },
  "admin@hotel.com": { password: "Admin123!", role: "Admin" },
  "maintenance@hotel.com": { password: "Agent123!", role: "MaintenanceAgent" },
  "roomservice@hotel.com": { password: "Agent123!", role: "RoomServiceAgent" },
  "servicebooking@hotel.com": { password: "Agent123!", role: "ServiceBookingAgent" },
  "wellness@hotel.com": { password: "Agent123!", role: "WellnessAgent" },
  "sos@hotel.com": { password: "Agent123!", role: "SOSAgent" },
};

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("guest@hotel.com");
  const [password, setPassword] = useState("Guest123!");
  const [error, setError] = useState("");
  const [showPolicy, setShowPolicy] = useState(true);
  const [scrolledToBottom, setScrolledToBottom] = useState(false);
  const [consentGiven, setConsentGiven] = useState(null);
  const contentRef = useRef(null);
  const navigate = useNavigate();

  const handleScroll = () => {
    const el = contentRef.current;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 10) {
      setScrolledToBottom(true);
    }
  };

  const handleConsent = () => {
    setConsentGiven(true);
    setShowPolicy(false);
  };

  const handleSkip = () => {
    setConsentGiven(false);
    setShowPolicy(false);
  };

  const handleLogin = () => {
    const user = dummyUsers[email];
    if (user && user.password === password) {
      const userData = {
        email,
        role: user.role,
        consent: consentGiven === true,
      };

      // Store data in localStorage
      localStorage.setItem("agent", user.role);
      localStorage.setItem("consent", userData.consent ? "true" : "false");
      localStorage.setItem("user", JSON.stringify(userData));

      // Reset guest room on fresh login
      if (user.role === "Guest") {
        localStorage.removeItem("roomNumber");
      }

      if (onLogin) onLogin(userData);
      navigate("/dashboard");
    } else {
      setError("Invalid credentials. Please try again.");
    }
  };

  return (
    <>
      <div className="d-flex align-items-center justify-content-center vh-100 bg-dark text-light animate__animated animate__fadeIn">
        <div className="p-4 bg-white rounded-4 shadow-lg text-dark" style={{ minWidth: "350px" }}>
          <h4 className="mb-4 text-center text-primary">🔐 Hotel AI Login</h4>
          <input
            type="email"
            className="form-control mb-3"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={showPolicy}
          />
          <input
            type="password"
            className="form-control mb-3"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={showPolicy}
          />
          {error && <div className="text-danger small mb-2">{error}</div>}
          <button className="btn btn-primary w-100" onClick={handleLogin} disabled={showPolicy}>
            Login
          </button>
        </div>
      </div>

      <Modal show={showPolicy} backdrop="static" centered size="lg">
        <Modal.Header>
          <Modal.Title>🛡️ Privacy Policy</Modal.Title>
        </Modal.Header>
        <Modal.Body ref={contentRef} onScroll={handleScroll} style={{ maxHeight: "60vh", overflowY: "auto" }}>
          <p><strong>Privacy Policy compliant with GDPR (EU/UK) and India’s DPDP Act 2023</strong></p>
          <p><strong>Last Updated:</strong> [Insert Date]</p>
          <p>Welcome to Hotel AI. Your privacy is important to us. This policy outlines how we collect, use, store, and protect your personal data in compliance with GDPR and India’s DPDP Act.</p>
          <hr />
          <p><strong>1. 📥 Data We Collect</strong></p>
          <ul>
            <li>Full name, email address, phone number</li>
            <li>Government-issued ID (for check-in verification)</li>
            <li>Booking details, payment details</li>
            <li>Chat interactions and service requests</li>
            <li>Location (if shared), health/disability data (with consent)</li>
          </ul>
          <p><strong>2. 🎯 Purpose of Collection</strong></p>
          <ul>
            <li>Facilitate hotel bookings and personalize experience</li>
            <li>Improve service via chat history</li>
            <li>Send updates (with consent)</li>
          </ul>
          <p><strong>3. ⚖️ Legal Basis for Processing</strong></p>
          <ul>
            <li>Consent - GDPR Art.6(1)(a), DPDP Section 5</li>
            <li>Contractual Necessity - GDPR Art.6(1)(b)</li>
            <li>Legal Obligation - GDPR Art.6(1)(c)</li>
            <li>Legitimate Interest - GDPR Art.6(1)(f)</li>
          </ul>
          <p><strong>4. ⏳ Data Retention</strong>: Stored only as long as necessary or upon deletion request.</p>
          <p><strong>5. 🌍 Storage</strong>: Stored securely in local/EU/India data centers.</p>
          <p><strong>6. 🔐 Security</strong>: Encryption, access control, regular audits.</p>
          <p><strong>7. 👶 Children’s Data</strong>: Not collected from users under 13 (India) or 16 (EU).</p>
          <p><strong>8. 📬 Contact</strong>: support@hotelai.app</p>
          <p><strong>9. 🔁 Policy Changes</strong>: You will be notified of changes via app/email.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleSkip}>Skip</Button>
          <Button variant="primary" onClick={handleConsent} disabled={!scrolledToBottom}>
            Accept & Continue
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
