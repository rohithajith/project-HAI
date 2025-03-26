import React, { createContext, useState, useEffect, useContext } from 'react';
import { notificationsApi } from '../services/api';
import socketService from '../services/socket';

// Create context
const NotificationContext = createContext();

// Custom hook to use the notification context
export const useNotifications = () => useContext(NotificationContext);

// Provider component
export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [roomNotifications, setRoomNotifications] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all notifications
  const fetchAllNotifications = async () => {
    try {
      setLoading(true);
      const response = await notificationsApi.getAll();
      setNotifications(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch notifications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch notifications for a specific room
  const fetchNotificationsByRoom = async (roomNumber) => {
    try {
      setLoading(true);
      const response = await notificationsApi.getByRoom(roomNumber);
      setRoomNotifications({
        ...roomNotifications,
        [roomNumber]: response.data.data.notifications
      });
      setError(null);
      return response.data.data.notifications;
    } catch (err) {
      setError(`Failed to fetch notifications for room ${roomNumber}`);
      console.error(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Create a new notification
  const createNotification = async (notificationData) => {
    try {
      const response = await notificationsApi.create(notificationData);
      const newNotification = response.data.data.notification;
      
      // Update notifications list
      setNotifications(prev => [newNotification, ...prev]);
      
      // Update room notifications if we have them loaded
      if (roomNotifications[newNotification.room_number]) {
        setRoomNotifications({
          ...roomNotifications,
          [newNotification.room_number]: [
            newNotification,
            ...roomNotifications[newNotification.room_number]
          ]
        });
      }
      
      return newNotification;
    } catch (err) {
      setError('Failed to create notification');
      console.error(err);
      throw err;
    }
  };

  // Mark a notification as read
  const markNotificationAsRead = async (id) => {
    try {
      const response = await notificationsApi.markAsRead(id);
      const updatedNotification = response.data.data.notification;
      
      // Update notifications list
      setNotifications(prev => 
        prev.map(notification => 
          notification.id === id ? updatedNotification : notification
        )
      );
      
      // Update room notifications if we have them loaded
      const roomNumber = updatedNotification.room_number;
      if (roomNotifications[roomNumber]) {
        setRoomNotifications({
          ...roomNotifications,
          [roomNumber]: roomNotifications[roomNumber].map(notification => 
            notification.id === id ? updatedNotification : notification
          )
        });
      }
      
      return updatedNotification;
    } catch (err) {
      setError(`Failed to mark notification ${id} as read`);
      console.error(err);
      throw err;
    }
  };

  // Send a laundry alert notification
  const sendLaundryAlert = async (roomNumber) => {
    try {
      const response = await notificationsApi.sendLaundryAlert(roomNumber);
      return response.data.data.notification;
    } catch (err) {
      setError(`Failed to send laundry alert for room ${roomNumber}`);
      console.error(err);
      throw err;
    }
  };

  // Initialize data and WebSocket listeners
  useEffect(() => {
    // Fetch initial data
    fetchAllNotifications();

    // Connect to WebSocket
    socketService.connect();

    // Listen for new notifications
    socketService.on('new_notification', (notification) => {
      // Update notifications list
      setNotifications(prev => [notification, ...prev]);
      
      // Update room notifications if we have them loaded
      const roomNumber = notification.room_number;
      if (roomNotifications[roomNumber]) {
        setRoomNotifications({
          ...roomNotifications,
          [roomNumber]: [notification, ...roomNotifications[roomNumber]]
        });
      }
    });

    // Listen for notifications being marked as read
    socketService.on('notifications_read', ({ roomNumber }) => {
      // Update all notifications
      setNotifications(prev => 
        prev.map(notification => 
          notification.room_number === roomNumber 
            ? { ...notification, is_read: true } 
            : notification
        )
      );
      
      // Update room notifications if we have them loaded
      if (roomNotifications[roomNumber]) {
        setRoomNotifications({
          ...roomNotifications,
          [roomNumber]: roomNotifications[roomNumber].map(notification => 
            ({ ...notification, is_read: true })
          )
        });
      }
    });

    // Cleanup
    return () => {
      socketService.off('new_notification');
      socketService.off('notifications_read');
    };
  }, [roomNotifications]);

  // Context value
  const value = {
    notifications,
    roomNotifications,
    loading,
    error,
    fetchAllNotifications,
    fetchNotificationsByRoom,
    createNotification,
    markNotificationAsRead,
    sendLaundryAlert
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;