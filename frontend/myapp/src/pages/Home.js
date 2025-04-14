import React, { useEffect, useState } from "react";
import Dashboard from "./Dashboard";
import ChatBot from "../components/ChatBot";
import CustomNavbar from "../components/Navbar" 
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [role, setRole] = useState(localStorage.getItem("agent"));
  const navigate = useNavigate();

  useEffect(() => {
    if (!role) navigate("/");
  }, [role]);

  return (
    <>
      <CustomNavbar role={role} onLogout={() => {
        localStorage.clear();
        setRole(null);
        navigate("/");
      }} />

      <div style={{ paddingTop: "4rem" }}>
        {role === "Guest" ? <ChatBot /> : <Dashboard agent={role} />}
      </div>

      {/* Floating Chatbot */}
      <div
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          zIndex: 9999,
        }}
      >
        <button
          className="btn btn-info rounded-circle shadow"
          onClick={() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })}
        >
          💬
        </button>
      </div>
    </>
  );
}
