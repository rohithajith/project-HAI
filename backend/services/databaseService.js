const db = require('../config/database');
const socketService = require('./socketService');

/**
 * Get all bookings
 * @returns {Promise<Array>} Array of booking objects
 */
async function getAllBookings() {
  try {
    return await db.all('SELECT * FROM bookings ORDER BY check_in DESC');
  } catch (error) {
    console.error('Error getting all bookings:', error);
    throw error;
  }
}

/**
 * Get upcoming bookings (check-in date is in the future)
 * @returns {Promise<Array>} Array of upcoming booking objects
 */
async function getUpcomingBookings() {
  try {
    return await db.all(
      'SELECT * FROM bookings WHERE check_in > datetime("now") ORDER BY check_in ASC'
    );
  } catch (error) {
    console.error('Error getting upcoming bookings:', error);
    throw error;
  }
}

/**
 * Get current bookings (check-in date is in the past and check-out date is in the future)
 * @returns {Promise<Array>} Array of current booking objects
 */
async function getCurrentBookings() {
  try {
    return await db.all(
      'SELECT * FROM bookings WHERE check_in <= datetime("now") AND check_out >= datetime("now") ORDER BY check_out ASC'
    );
  } catch (error) {
    console.error('Error getting current bookings:', error);
    throw error;
  }
}

/**
 * Get past bookings (check-out date is in the past)
 * @returns {Promise<Array>} Array of past booking objects
 */
async function getPastBookings() {
  try {
    return await db.all(
      'SELECT * FROM bookings WHERE check_out < datetime("now") ORDER BY check_out DESC'
    );
  } catch (error) {
    console.error('Error getting past bookings:', error);
    throw error;
  }
}

/**
 * Get booking by ID
 * @param {number} id - Booking ID
 * @returns {Promise<Object>} Booking object
 */
async function getBookingById(id) {
  try {
    return await db.get('SELECT * FROM bookings WHERE id = ?', [id]);
  } catch (error) {
    console.error(`Error getting booking with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Create a new alert
 * @param {Object} alert - Alert object
 * @returns {Promise<Object>} Created alert object with ID
 */
async function createAlert(alert) {
  try {
    const { type, message, room_number } = alert;
    
    const result = await db.run(
      'INSERT INTO alerts (type, message, room_number) VALUES (?, ?, ?)',
      [type, message, room_number]
    );
    
    // Get the created alert
    const createdAlert = await db.get('SELECT * FROM alerts WHERE id = ?', [result.lastID]);
    
    // Notify connected clients about the new alert
    const io = socketService.getIO();
    if (io) {
      io.emit('new_alert', createdAlert);
    }
    
    return createdAlert;
  } catch (error) {
    console.error('Error creating alert:', error);
    throw error;
  }
}

/**
 * Get all alerts
 * @returns {Promise<Array>} Array of alert objects
 */
async function getAllAlerts() {
  try {
    return await db.all('SELECT * FROM alerts ORDER BY created_at DESC');
  } catch (error) {
    console.error('Error getting all alerts:', error);
    throw error;
  }
}

/**
 * Resolve an alert
 * @param {number} id - Alert ID
 * @returns {Promise<Object>} Updated alert object
 */
async function resolveAlert(id) {
  try {
    await db.run('UPDATE alerts SET is_resolved = 1 WHERE id = ?', [id]);
    
    // Get the updated alert
    const updatedAlert = await db.get('SELECT * FROM alerts WHERE id = ?', [id]);
    
    // Notify connected clients about the resolved alert
    const io = socketService.getIO();
    if (io) {
      io.emit('alert_resolved', updatedAlert);
    }
    
    return updatedAlert;
  } catch (error) {
    console.error(`Error resolving alert with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Create a new notification
 * @param {Object} notification - Notification object
 * @returns {Promise<Object>} Created notification object with ID
 */
async function createNotification(notification) {
  try {
    const { room_number, message } = notification;
    
    const result = await db.run(
      'INSERT INTO notifications (room_number, message) VALUES (?, ?)',
      [room_number, message]
    );
    
    // Get the created notification
    const createdNotification = await db.get('SELECT * FROM notifications WHERE id = ?', [result.lastID]);
    
    // Notify connected clients about the new notification
    const io = socketService.getIO();
    if (io) {
      io.emit('new_notification', createdNotification);
    }
    
    return createdNotification;
  } catch (error) {
    console.error('Error creating notification:', error);
    throw error;
  }
}

/**
 * Get all notifications
 * @returns {Promise<Array>} Array of notification objects
 */
async function getAllNotifications() {
  try {
    return await db.all('SELECT * FROM notifications ORDER BY created_at DESC');
  } catch (error) {
    console.error('Error getting all notifications:', error);
    throw error;
  }
}

/**
 * Get notifications for a specific room
 * @param {string} roomNumber - Room number
 * @returns {Promise<Array>} Array of notification objects for the specified room
 */
async function getNotificationsByRoom(roomNumber) {
  try {
    return await db.all(
      'SELECT * FROM notifications WHERE room_number = ? ORDER BY created_at DESC',
      [roomNumber]
    );
  } catch (error) {
    console.error(`Error getting notifications for room ${roomNumber}:`, error);
    throw error;
  }
}

/**
 * Mark a notification as read
 * @param {number} id - Notification ID
 * @returns {Promise<Object>} Updated notification object
 */
async function markNotificationAsRead(id) {
  try {
    await db.run('UPDATE notifications SET is_read = 1 WHERE id = ?', [id]);
    
    // Get the updated notification
    const updatedNotification = await db.get('SELECT * FROM notifications WHERE id = ?', [id]);
    
    return updatedNotification;
  } catch (error) {
    console.error(`Error marking notification with ID ${id} as read:`, error);
    throw error;
  }
}

module.exports = {
  getAllBookings,
  getUpcomingBookings,
  getCurrentBookings,
  getPastBookings,
  getBookingById,
  createAlert,
  getAllAlerts,
  resolveAlert,
  createNotification,
  getAllNotifications,
  getNotificationsByRoom,
  markNotificationAsRead
};