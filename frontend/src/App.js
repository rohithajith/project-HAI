import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import GuestChatbotPage from './pages/GuestChatbotPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import RoomServiceDashboardPage from './pages/RoomServiceDashboardPage';
import './App.css'; // We'll create this next

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Guest Chatbot</Link>
            </li>
            <li>
              <Link to="/admin">Admin Dashboard</Link>
            </li>
            <li>
              <Link to="/room-service">Room Service Dashboard</Link>
            </li>
          </ul>
        </nav>

        <hr />

        {/* A <Routes> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Routes>
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/room-service" element={<RoomServiceDashboardPage />} />
          <Route path="/" element={<GuestChatbotPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;