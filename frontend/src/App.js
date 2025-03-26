import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
// Removed unused: import Dashboard from './pages/Dashboard';
// Removed unused: import Bookings from './pages/Bookings';
// Removed unused: import Notifications from './pages/Notifications';
// Removed unused: import Alerts from './pages/Alerts';
import AdminDashboard from './pages/AdminDashboard'; // Import AdminDashboard
import GuestPage from './pages/GuestPage'; // Import GuestPage
import LandingPage from './pages/LandingPage';
<<<<<<< HEAD
import Layout from './components/common/Layout'; // Layout for Admin section
=======
import GuestLandingPage from './pages/GuestLandingPage';
import Layout from './components/common/Layout';
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
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
<<<<<<< HEAD
              {/* LandingPage (Login Selector) is the entry point, no Layout */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} /> {/* Consider if guest registration is needed */}
=======
              <Route path="/" element={<Layout><LandingPage /></Layout>} />
              <Route path="/guest" element={<Layout><GuestLandingPage /></Layout>} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/unauthorized" element={<Unauthorized />} />

<<<<<<< HEAD
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
=======
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
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
              <Route
                element={
                  <ProtectedRoute
                    allowedRoles={['admin', 'manager', 'staff']}
<<<<<<< HEAD
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

=======
                    redirectPath="/unauthorized"
                  />
                }
              >
                <Route element={<Layout />}>
                  <Route path="/admin/dashboard" element={<Dashboard />} />
                  {/* Add more admin routes here */}
                </Route>
              </Route>
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
            </Routes>
          </Router>
        </NotificationProvider>
      </AlertProvider>
    </AuthProvider>
  );
}

export default App;
