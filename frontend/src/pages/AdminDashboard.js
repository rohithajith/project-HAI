import React from 'react';
import AdminNotificationList from '../components/notifications/AdminNotificationList';
// Import other admin components as needed, e.g., for bookings
// import AdminBookings from '../components/admin/AdminBookings';
import './DashboardStyles.css'; // Use shared dashboard styles

function AdminDashboard() {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>System Overview and Notifications</p>
      </header>
      <main className="dashboard-content">
        {/* Section for real-time notifications */}
        <AdminNotificationList />

        {/* Placeholder for other admin sections like booking management */}
        {/* <section className="card">
          <h2 className="card-header">Booking Management</h2>
          <div style={{padding: '1rem'}}>
             <AdminBookings /> // Example component
          </div>
        </section> */}

        {/* Add more sections as needed */}

      </main>
      <footer className="dashboard-footer">
        Hotel AI Management System - Admin Panel
      </footer>
    </div>
  );
}

export default AdminDashboard;