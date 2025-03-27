import React from 'react';
import RoomServiceNotificationList from '../components/notifications/RoomServiceNotificationList';
import './DashboardStyles.css'; // Shared dashboard styles (will create later)

function RoomServiceDashboard() {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Room Service Dashboard</h1>
        <p>Real-time updates for room service requests</p>
      </header>
      <main className="dashboard-content">
        <RoomServiceNotificationList />
      </main>
      <footer className="dashboard-footer">
        Hotel AI Management System
      </footer>
    </div>
  );
}

export default RoomServiceDashboard;