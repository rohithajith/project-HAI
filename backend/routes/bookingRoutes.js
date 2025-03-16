const express = require('express');
const bookingController = require('../controllers/bookingController');

const router = express.Router();

// Get all bookings
router.get('/', bookingController.getAllBookings);

// Get upcoming bookings
router.get('/upcoming', bookingController.getUpcomingBookings);

// Get current bookings
router.get('/current', bookingController.getCurrentBookings);

// Get past bookings
router.get('/past', bookingController.getPastBookings);

// Get booking by ID
router.get('/:id', bookingController.getBookingById);

module.exports = router;