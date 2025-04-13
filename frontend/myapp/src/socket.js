// src/socket.js
import { io } from "socket.io-client";

// 🔁 Replace with your server IP if needed
const socket = io("http://localhost:8000", {
  transports: ["websocket"],
  path: "/socket.io",
});

export default socket;
