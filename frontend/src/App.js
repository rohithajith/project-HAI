import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AdminDashboard from './pages/AdminDashboard'; // Import AdminDashboard
import GuestPage from './pages/GuestPage'; // Import GuestPage
import LandingPage from './pages/LandingPage'; // Login Selector Page
import RoomServiceDashboard from './pages/RoomServiceDashboard'; // Import Room Service Dashboard
import Layout from './components/common/Layout'; // Layout for Admin/Staff sections
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ForgotPassword from './components/auth/ForgotPassword';
import ResetPassword from './components/auth/ResetPassword';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { AlertProvider } from './contexts/AlertContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { SocketProvider } from './contexts/SocketContext'; // Import SocketProvider
import './App.css';

// Unauthorized component
const Unauthorized = () => (
  <div style={{ padding: '2rem', textAlign: 'center' }}>
    <h1>Unauthorized</h1>
    <p>You do not have permission to access this page.</p>
  </div>
);

// Placeholder for 404 Not Found
const NotFoundPage = () => (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>404 - Not Found</h1>
      <p>The page you are looking for does not exist.</p>
    </div>
);


function App() {
  return (
    <AuthProvider>
      <AlertProvider>
        <NotificationProvider>
          {/* Wrap with SocketProvider to make socket available */}
          <SocketProvider>
            <Router>
              <Routes>
                {/* Public routes */}
                {/* LandingPage (Login Selector) is the entry point, no Layout */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<Login />} />
                {/* Registration might be admin-controlled or public depending on requirements */}
                <Route path="/register" element={<Register />} />
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
                      allowedRoles={['admin', 'manager', 'staff', 'room_service']} // Added room_service role
                      redirectPath="/login" // Redirect staff/admin to login if not authenticated
                    />
                  }
                >
                  {/* Staff/Admin sections use the main Layout */}
                  <Route element={<Layout />}>
                    <Route path="/admin/dashboard" element={<AdminDashboard />} />
                    {/* Add Room Service Dashboard route */}
                    <Route path="/room-service/dashboard" element={<RoomServiceDashboard />} />

                    {/* Add other admin/staff-specific routes here, wrapped in Layout */}
                    {/* Example: <Route path="/admin/bookings" element={<AdminBookingsPage />} /> */}
                    {/* Example: <Route path="/admin/users" element={<AdminUsersPage />} /> */}
                  </Route>
                </Route>

                {/* Optional: Catch-all route for 404 Not Found */}
                <Route path="*" element={<NotFoundPage />} />

              </Routes>
            </Router>
          </SocketProvider>
        </NotificationProvider>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;
