import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
// Removed unused: import Dashboard from './pages/Dashboard';
// Removed unused: import Bookings from './pages/Bookings';
// Removed unused: import Notifications from './pages/Notifications';
// Removed unused: import Alerts from './pages/Alerts';
import AdminDashboard from './pages/AdminDashboard'; // Import AdminDashboard
import GuestPage from './pages/GuestPage'; // Import GuestPage
import LandingPage from './pages/LandingPage';
import Layout from './components/common/Layout'; // Layout for Admin section
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
              {/* LandingPage (Login Selector) is the entry point, no Layout */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} /> {/* Consider if guest registration is needed */}
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/unauthorized" element={<Unauthorized />} />

              {/* Protected routes for GUESTS */}
              <Route
                element={
                  <ProtectedRoute
                    allowedRoles={['guest']} // Assuming 'guest' role exists
                    redirectPath="/login" // Redirect guests to login if not authenticated
                  />
                }
              >
                {/* GuestPage does not use the main Layout */}
                <Route path="/guest" element={<GuestPage />} />
              </Route>

              {/* Protected routes for STAFF/ADMIN */}
              <Route
                element={
                  <ProtectedRoute
                    allowedRoles={['admin', 'manager', 'staff']}
                    redirectPath="/login" // Redirect staff/admin to login if not authenticated
                  />
                }
              >
                {/* Admin section uses the main Layout */}
                <Route element={<Layout />}>
                  <Route path="/admin/dashboard" element={<AdminDashboard />} />
                  {/* Add other admin-specific routes here, wrapped in Layout */}
                  {/* Example: <Route path="/admin/bookings" element={<AdminBookingsPage />} /> */}
                  {/* Example: <Route path="/admin/users" element={<AdminUsersPage />} /> */}
                </Route>
              </Route>

              {/* Optional: Catch-all route for 404 Not Found */}
              {/* <Route path="*" element={<NotFoundPage />} /> */}

            </Routes>
          </Router>
        </NotificationProvider>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;
