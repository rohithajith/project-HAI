import React, { useState, useEffect, useContext } from 'react';
import { SocketContext } from '../../contexts/SocketContext';
// import './NotificationList.css'; // Styles are now in DashboardStyles.css

function AdminNotificationList() {
  const socket = useContext(SocketContext);
  const [notifications, setNotifications] = useState([]);

  // Define the events this dashboard listens to (matching Python agent output)
  const relevantEvents = [
    'maintenance_report', // Changed from maintenance_issue_report
    'maintenance_schedule',
    // Add other relevant events like 'admin_booking_spa', 'admin_booking_cab', 'system_alert' when implemented
  ];

  useEffect(() => {
    if (!socket) {
      console.warn('Socket not available in AdminNotificationList');
      return;
    }

    console.log('Setting up Admin notification listeners...');

    const handleNewNotification = (data) => {
      console.log('Received Admin Notification:', data);
      const newNotification = {
        ...data,
        id: `${Date.now()}-${Math.random()}`,
        timestamp: new Date(),
        type: data.event || 'admin_notification', // Use event name as type
      };
      setNotifications(prev => [newNotification, ...prev]);
    };

    relevantEvents.forEach(event => {
      socket.on(event, handleNewNotification);
    });

    return () => {
      console.log('Cleaning up Admin notification listeners...');
      relevantEvents.forEach(event => {
        socket.off(event, handleNewNotification);
      });
    };
  }, [socket]);

  const formatTimestamp = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  // Function to render notification details based on type
  const renderNotificationDetails = (notification) => {
    const payload = notification.payload || {};
    switch (notification.type) {
      case 'maintenance_issue_report':
        return `Maintenance Issue: ${payload.description || 'N/A'} (Type: ${payload.issue_type || 'N/A'}, Urgency: ${payload.urgency || 'N/A'})`;
      case 'maintenance_schedule':
         return `Maintenance Scheduled: ${payload.description || 'N/A'} (Type: ${payload.issue_type || 'N/A'}, Time: ${payload.preferred_time || 'N/A'})`;
      // Add cases for other types (bookings, alerts) here
      default:
        return `System Notification: ${JSON.stringify(payload)}`;
    }
  };


  return (
    <div className="notification-list-container card">
      <h2 className="card-header">System Notifications & Alerts</h2>
      {notifications.length === 0 ? (
        <p className="no-notifications">No new system notifications.</p>
      ) : (
        <ul className="notification-list">
          {notifications.map((notification) => (
            <li key={notification.id} className={`notification-item notification-${notification.type}`}>
              <span className="notification-time">{formatTimestamp(notification.timestamp)}</span>
              <span className="notification-room">Room: <strong>{notification.payload?.roomNumber || 'System'}</strong></span> {/* Show 'System' if no room number */}
              <p className="notification-message">{renderNotificationDetails(notification)}</p>
              {/* Add admin-specific actions if needed */}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default AdminNotificationList;