const NotificationService = require('../services/notificationService');

const createNotification = async (req, res) => {
  try {
    const { type, message, guestId } = req.body;
    if (!type || !message || !guestId) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    const notification = await NotificationService.create({
      type,
      message,
      guestId,
      status: 'unread',
    });
    res.status(201).json(notification);
  } catch (error) {
    console.error('Error creating notification:', error);
    res.status(500).json({ error: 'Failed to create notification' });
  }
};

const getAllNotifications = async (req, res) => {
  try {
    const notifications = await NotificationService.getAll();
    res.status(200).json(notifications);
  } catch (error) {
    console.error('Error getting notifications:', error);
    res.status(500).json({ error: 'Failed to get notifications' });
  }
};

const getNotificationsByRoom = async (req, res) => {
  try {
    const { roomNumber } = req.params;
    const notifications = await NotificationService.getByRoom(roomNumber);
    res.status(200).json(notifications);
  } catch (error) {
    console.error('Error getting room notifications:', error);
    res.status(500).json({ error: 'Failed to get room notifications' });
  }
};

const markNotificationAsRead = async (req, res) => {
  try {
    const { id } = req.params;
    const notification = await NotificationService.markAsRead(id);
    res.status(200).json(notification);
  } catch (error) {
    console.error('Error marking notification as read:', error);
    res.status(500).json({ error: 'Failed to mark notification as read' });
  }
};

const sendLaundryAlert = async (req, res) => {
  try {
    const { roomNumber, message } = req.body;
    const notification = await NotificationService.createLaundryAlert(roomNumber, message);
    res.status(201).json(notification);
  } catch (error) {
    console.error('Error sending laundry alert:', error);
    res.status(500).json({ error: 'Failed to send laundry alert' });
  }
};

module.exports = {
  createNotification,
  getAllNotifications,
  getNotificationsByRoom,
  markNotificationAsRead,
  sendLaundryAlert
};