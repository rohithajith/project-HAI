const express = require('express');
const notificationController = require('../controllers/notificationController');

const router = express.Router();

// Get all notifications
router.get('/', notificationController.getAllNotifications);

// Create a new notification
router.post('/', notificationController.createNotification);

// Get notifications for a specific room
router.get('/room/:roomNumber', notificationController.getNotificationsByRoom);

// Mark a notification as read
router.put('/:id/read', notificationController.markNotificationAsRead);

// Send a laundry alert notification
router.post('/laundry', notificationController.sendLaundryAlert);

module.exports = router;