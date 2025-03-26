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
<<<<<<< HEAD
    console.log("NotificationService:", NotificationService);
        const notifications = await NotificationService.getUnreadNotifications(); // Changed getAllNotifications to getUnreadNotifications
    res.status(200).json(notifications);
  } catch (error) {
    console.error('Error getting all notifications:', error);
=======
    const notifications = await NotificationService.getAll();
    res.status(200).json(notifications);
  } catch (error) {
    console.error('Error getting notifications:', error);
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
    res.status(500).json({ error: 'Failed to get notifications' });
  }
};

const getNotificationsByRoom = async (req, res) => {
  try {
    const { roomNumber } = req.params;
<<<<<<< HEAD
    // Assuming guestId can be derived from roomNumber or requires another lookup
    // This might need adjustment based on how rooms relate to guests
    // For now, let's assume a service method exists or needs to be created
    // const guestId = await findGuestIdByRoom(roomNumber);
    // const notifications = await NotificationService.getByGuestId(guestId);
    // Placeholder:
    console.warn(`getNotificationsByRoom needs implementation to link room ${roomNumber} to guestId`);
    res.status(501).json({ error: 'Not Implemented: Cannot yet fetch notifications by room number.' });
  } catch (error) {
    console.error('Error getting notifications by room:', error);
    res.status(500).json({ error: 'Failed to get notifications by room' });
=======
    const notifications = await NotificationService.getByRoom(roomNumber);
    res.status(200).json(notifications);
  } catch (error) {
    console.error('Error getting room notifications:', error);
    res.status(500).json({ error: 'Failed to get room notifications' });
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
  }
};

const markNotificationAsRead = async (req, res) => {
  try {
    const { id } = req.params;
<<<<<<< HEAD
    const updatedNotification = await NotificationService.markAsRead(id);
    if (!updatedNotification) {
      return res.status(404).json({ error: 'Notification not found' });
    }
    res.status(200).json(updatedNotification);
=======
    const notification = await NotificationService.markAsRead(id);
    res.status(200).json(notification);
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
  } catch (error) {
    console.error('Error marking notification as read:', error);
    res.status(500).json({ error: 'Failed to mark notification as read' });
  }
};

const sendLaundryAlert = async (req, res) => {
  try {
<<<<<<< HEAD
    const { guestId, message } = req.body; // Assuming guestId and message are provided
    if (!guestId || !message) {
      return res.status(400).json({ error: 'Missing guestId or message for laundry alert' });
    }
    const notification = await NotificationService.create({
      type: 'laundry_alert',
      message: message,
      guestId: guestId,
      status: 'unread',
    });
    // Potentially add logic here to push this notification via WebSocket or similar
=======
    const { roomNumber, message } = req.body;
    const notification = await NotificationService.createLaundryAlert(roomNumber, message);
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
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
<<<<<<< HEAD
  sendLaundryAlert,
=======
  sendLaundryAlert
>>>>>>> e1460d6789cb070325e1e5df2a7091b6fedf1639
};