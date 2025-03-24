import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Bookings from './pages/Bookings';
import Notifications from './pages/Notifications';
import Alerts from './pages/Alerts';
import LandingPage from './pages/LandingPage';
import GuestPage from './pages/GuestPage';
import AdminLandingPage from './pages/AdminLandingPage';
import GuestLandingPage from './pages/GuestLandingPage';
import GuestLayout from './components/common/GuestLayout';
import AdminLayout from './components/common/AdminLayout';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import './App.css';

// Unauthorized component
const Unauthorized = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h1>Unauthorized</h1>
    <p>You do not have permission to access this page.</p>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Router>
          <Routes>
            {/* Public landing page - redirects based on user type */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Authentication routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/unauthorized" element={<Unauthorized />} />
            
            {/* Guest routes - completely separate from admin */}
            <Route path="/guest" element={
              <ProtectedRoute 
                allowedRoles={['guest']} 
                redirectPath="/login"
              />
            }>
              <Route element={<GuestLayout />}>
                <Route index element={<GuestLandingPage />} />
                <Route path="chatbot" element={<GuestPage />} />
                <Route path="services" element={<GuestPage />} />
              </Route>
            </Route>
            
            {/* Admin routes - completely separate from guest */}
            <Route path="/admin" element={
              <ProtectedRoute
                allowedRoles={['admin', 'manager', 'staff']}
                redirectPath="/unauthorized"
              />
            }>
              <Route element={<AdminLayout />}>
                <Route index element={<AdminLandingPage />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="bookings" element={<Bookings />} />
                <Route path="notifications" element={<Notifications />} />
                <Route path="alerts" element={<Alerts />} />
              </Route>
            </Route>
            
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AppProvider>
    </AuthProvider>
  );
}

export default App;
