import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Bookings from './pages/Bookings';
import Notifications from './pages/Notifications';
import Alerts from './pages/Alerts';
import LandingPage from './pages/LandingPage';
import GuestLandingPage from './pages/GuestLandingPage';
import Layout from './components/common/Layout';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { AlertProvider } from './contexts/AlertContext';
import { NotificationProvider } from './contexts/NotificationContext';
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
      <AlertProvider>
        <NotificationProvider>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Layout><LandingPage /></Layout>} />
              <Route path="/guest" element={<Layout><GuestLandingPage /></Layout>} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/unauthorized" element={<Unauthorized />} />

              {/* Protected routes for all authenticated users */}
              <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/bookings" element={<Bookings />} />
                  <Route path="/notifications" element={<Notifications />} />
                  <Route path="/alerts" element={<Alerts />} />
                </Route>
              </Route>

              {/* Protected routes for staff and admin */}
              <Route
                element={
                  <ProtectedRoute
                    allowedRoles={['admin', 'manager', 'staff']}
                    redirectPath="/unauthorized"
                  />
                }
              >
                <Route element={<Layout />}>
                  <Route path="/admin/dashboard" element={<Dashboard />} />
                  {/* Add more admin routes here */}
                </Route>
              </Route>
            </Routes>
          </Router>
        </NotificationProvider>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;
