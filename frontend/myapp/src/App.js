// import React, { useEffect, useState } from "react";
// import ChatBot from "./components/ChatBot";
// import Dashboard from "./pages/Dashboard";
// import CustomNavbar from "./components/Navbar";
// import "bootstrap/dist/css/bootstrap.min.css";
// import "animate.css";

// function App() {
//   const [agent, setAgent] = useState(localStorage.getItem("agent") || null);

//   useEffect(() => {
//     if (agent) localStorage.setItem("agent", agent);
//   }, [agent]);

//   if (!agent) {
//     return (
//       <div className="text-center mt-5">
//         <h3>Select Your Role</h3>
//         {["Guest", "RoomServiceAgentAgent", "MaintenanceAgentAgent", "WellnessAgentAgent", "Admin"].map((role) => (
//           <button
//             key={role}
//             onClick={() => setAgent(role)}
//             className="btn btn-outline-primary m-2"
//           >
//             {role}
//           </button>
//         ))}
//       </div>
//     );
//   }

//   return (
//     <div>
//       <CustomNavbar role={agent} onLogout={() => setAgent(null)} />
//       {agent === "Guest" ? <ChatBot /> : <Dashboard agent={agent} />}
//       <button
//         onClick={() => {
//           localStorage.removeItem("agent");
//           localStorage.removeItem("roomNumber");
//           window.location.reload();
//         }}
//         style={{
//           position: "fixed",
//           top: 10,
//           right: 10,
//           padding: "8px 12px",
//           backgroundColor: "#dc3545",
//           color: "white",
//           border: "none",
//           borderRadius: "5px",
//           zIndex: 9999,
//         }}
//       >
//         Reset Role
//       </button>
//     </div>
//   );
// }

// export default App;

import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPage from './pages/Login';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ChatBot from './components/ChatBot';

function App() {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user')));

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <Routes>
      <Route path="/" element={<LoginPage onLogin={handleLogin} />} />
      <Route path="/dashboard" element={<Home user={user} onLogout={handleLogout} />} />
      <Route path="/chatbot" element={<ChatBot user={user} onLogout={handleLogout} />} />
      <Route path="*" element={<div className="p-5 text-center">404 Not Found</div>} />
    </Routes>
  );
}

export default App;

