const express = require('express');
const alertController = require('../controllers/alertController');

const router = express.Router();

// Get all alerts
router.get('/', alertController.getAllAlerts);

// Get current alert count
router.get('/count', alertController.getAlertCount);

// Create a new alert
router.post('/', alertController.createAlert);

// Resolve an alert
router.put('/:id/resolve', alertController.resolveAlert);

// Reset alert counter
router.post('/reset', alertController.resetAlertCount);

module.exports = router;