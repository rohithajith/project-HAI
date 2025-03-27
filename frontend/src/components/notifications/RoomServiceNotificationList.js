import React, { useState, useEffect, useContext } from 'react';
import { SocketContext } from '../../contexts/SocketContext'; // Assuming a SocketContext exists
// import './NotificationList.css'; // Styles are now in DashboardStyles.css

function RoomServiceNotificationList() {
  const socket = useContext(SocketContext);
  const [notifications, setNotifications] = useState([]);

  // Define the events this dashboard listens to (matching Python agent output)
  const relevantEvents = [
    'room_service_food', // Changed from room_service_food_order
    'room_service_drink', // Changed from room_service_drink_order
    // Add other relevant events like 'room_service_request_towel', 'room_service_request_cleaning' when implemented
  ];

  useEffect(() => {
    if (!socket) {
      console.warn('Socket not available in RoomServiceNotificationList');
      return;
    }

    console.log('Setting up Room Service notification listeners...');

    const handleNewNotification = (data) => {
      console.log('Received Room Service Notification:', data);
      // Add timestamp and unique ID for rendering
      const newNotification = {
        ...data,
        id: `${Date.now()}-${Math.random()}`, // Simple unique ID
        timestamp: new Date(),
        type: data.event || 'room_service', // Use event name as type or default
      };
      // Add to the beginning of the list
      setNotifications(prev => [newNotification, ...prev]);
    };

    // Register listeners for relevant events
    relevantEvents.forEach(event => {
      socket.on(event, handleNewNotification);
    });

    // Cleanup listeners on component unmount
    return () => {
      console.log('Cleaning up Room Service notification listeners...');
      relevantEvents.forEach(event => {
        socket.off(event, handleNewNotification);
      });
    };
  }, [socket]); // Re-run effect if socket instance changes

  const formatTimestamp = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  // Function to render notification details based on type
  const renderNotificationDetails = (notification) => {
    const payload = notification.payload || {};
    switch (notification.type) {
      case 'room_service_food_order':
        return `Food Order: ${payload.items?.join(', ') || 'N/A'}. Instructions: ${payload.instructions || 'None'}`;
      case 'room_service_drink_order':
        return `Drink Order: ${payload.beverages?.join(', ') || 'N/A'}. Ice: ${payload.ice_preference || 'Regular'}`;
      // Add cases for other types (towels, cleaning) here
      default:
        return `Unknown Request: ${JSON.stringify(payload)}`;
    }
  };

  return (
    <div className="notification-list-container card">
      <h2 className="card-header">Incoming Requests</h2>
      {notifications.length === 0 ? (
        <p className="no-notifications">No new room service requests.</p>
      ) : (
        <ul className="notification-list">
          {notifications.map((notification) => (
            <li key={notification.id} className={`notification-item notification-${notification.type}`}>
              <span className="notification-time">{formatTimestamp(notification.timestamp)}</span>
              <span className="notification-room">Room: <strong>{notification.payload?.roomNumber || 'N/A'}</strong></span>
              <p className="notification-message">{renderNotificationDetails(notification)}</p>
              {/* Add buttons for actions like 'Acknowledge', 'Complete' later */}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RoomServiceNotificationList;