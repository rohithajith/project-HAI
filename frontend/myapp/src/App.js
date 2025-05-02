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

