import React, { useEffect, useState } from "react";
import socket from "../socket";

const ConnectionStatus = () => {
  const [status, setStatus] = useState("🔴 Disconnected");

  useEffect(() => {
    socket.onopen = () => {
      console.log("✅ Connected to WebSocket");
      setStatus("🟢 Connected");
    };

    socket.onclose = () => {
      console.log("❌ Disconnected");
      setStatus("🔴 Disconnected");
    };

    socket.onerror = (error) => {
      console.error("⚠️ WebSocket Error:", error);
      setStatus("🔴 Error Connecting");
    };
  }, []);

  return <p>Status: {status}</p>;
};

export default ConnectionStatus;
