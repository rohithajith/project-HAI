const databaseService = require('../services/databaseService');
const socketService = require('../services/socketService');

/**
 * Get all alerts
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getAllAlerts = async (req, res, next) => {
  try {
    const alerts = await databaseService.getAllAlerts();
    
    res.status(200).json({
      status: 'success',
      results: alerts.length,
      data: {
        alerts
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get current alert count
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.getAlertCount = async (req, res, next) => {
  try {
    const count = socketService.getAlertCount();
    
    res.status(200).json({
      status: 'success',
      data: {
        count
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Create a new alert
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.createAlert = async (req, res, next) => {
  try {
    // Validate request body
    if (!req.body.type) {
      return res.status(400).json({
        status: 'fail',
        message: 'Alert type is required'
      });
    }
    
    // Create alert in database
    const alert = await databaseService.createAlert({
      type: req.body.type,
      message: req.body.message,
      room_number: req.body.room_number
    });
    
    // Increment alert counter
    socketService.getIO().emit('trigger_alert');
    
    res.status(201).json({
      status: 'success',
      data: {
        alert
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Resolve an alert
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.resolveAlert = async (req, res, next) => {
  try {
    const alert = await databaseService.resolveAlert(req.params.id);
    
    if (!alert) {
      return res.status(404).json({
        status: 'fail',
        message: `No alert found with ID: ${req.params.id}`
      });
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        alert
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Reset alert counter
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next middleware function
 */
exports.resetAlertCount = async (req, res, next) => {
  try {
    const count = socketService.resetAlertCount();
    
    res.status(200).json({
      status: 'success',
      data: {
        count
      }
    });
  } catch (error) {
    next(error);
  }
};