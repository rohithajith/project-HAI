const databaseService = require('../services/databaseService');
const socketService = require('../services/socketService');

/**
 * Get all bookings
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getAllBookings = async (req, res, next) => {
  try {
    const bookings = await databaseService.getAllBookings();
    
    res.status(200).json({
      status: 'success',
      results: bookings.length,
      data: {
        bookings
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get upcoming bookings
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getUpcomingBookings = async (req, res, next) => {
  try {
    const bookings = await databaseService.getUpcomingBookings();
    
    res.status(200).json({
      status: 'success',
      results: bookings.length,
      data: {
        bookings
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get current bookings
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getCurrentBookings = async (req, res, next) => {
  try {
    const bookings = await databaseService.getCurrentBookings();
    
    res.status(200).json({
      status: 'success',
      results: bookings.length,
      data: {
        bookings
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get past bookings
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getPastBookings = async (req, res, next) => {
  try {
    const bookings = await databaseService.getPastBookings();
    
    res.status(200).json({
      status: 'success',
      results: bookings.length,
      data: {
        bookings
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get booking by ID
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getBookingById = async (req, res, next) => {
  try {
    const booking = await databaseService.getBookingById(req.params.id);
    
    if (!booking) {
      return res.status(404).json({
        status: 'fail',
        message: `No booking found with ID: ${req.params.id}`
      });
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        booking
      }
    });
  } catch (error) {
    next(error);
  }
};