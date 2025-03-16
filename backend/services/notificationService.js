const databaseService = require('./databaseService');
const socketService = require('./socketService');

/**
 * Send a notification to a specific room
 * @param {string} roomNumber - Room number
 * @param {string} message - Notification message
 * @returns {Promise<Object>} Created notification object
 */
async function sendRoomNotification(roomNumber, message) {
  try {
    // Create notification in database
    const notification = await databaseService.createNotification({
      room_number: roomNumber,
      message
    });
    
    // Send notification via WebSocket
    const io = socketService.getIO();
    if (io) {
      io.to(`room_${roomNumber}`).emit('new_notification', notification);
      
      // Also broadcast to all clients for the notifications tab
      io.emit('notification_created', notification);
    }
    
    return notification;
  } catch (error) {
    console.error('Error sending room notification:', error);
    throw error;
  }
}

/**
 * Send a laundry alert notification
 * @param {string} roomNumber - Room number
 * @returns {Promise<Object>} Created notification object
 */
async function sendLaundryAlert(roomNumber) {
  return await sendRoomNotification(roomNumber, 'Laundry service requested');
}

/**
 * Get all unread notifications
 * @returns {Promise<Array>} Array of unread notification objects
 */
async function getUnreadNotifications() {
  try {
    // Use databaseService instead of direct db access
    const allNotifications = await databaseService.getAllNotifications();
    return allNotifications.filter(notification => !notification.is_read);
  } catch (error) {
    console.error('Error getting unread notifications:', error);
    throw error;
  }
}

/**
 * Mark all notifications for a room as read
 * @param {string} roomNumber - Room number
 * @returns {Promise<number>} Number of notifications marked as read
 */
async function markAllNotificationsAsReadForRoom(roomNumber) {
  try {
    // Get all unread notifications for the room
    const notifications = await databaseService.getNotificationsByRoom(roomNumber);
    const unreadNotifications = notifications.filter(notification => !notification.is_read);
    
    // Mark each notification as read
    const updatePromises = unreadNotifications.map(notification => 
      databaseService.markNotificationAsRead(notification.id)
    );
    
    await Promise.all(updatePromises);
    
    // Notify connected clients
    const io = socketService.getIO();
    if (io) {
      io.emit('notifications_read', { roomNumber });
    }
    
    return unreadNotifications.length;
  } catch (error) {
    console.error(`Error marking notifications as read for room ${roomNumber}:`, error);
    throw error;
  }
}

module.exports = {
  sendRoomNotification,
  sendLaundryAlert,
  getUnreadNotifications,
  markAllNotificationsAsReadForRoom
};