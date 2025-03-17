const jwt = require('jsonwebtoken');
const db = require('../config/database');

// Environment variables
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_key';

/**
 * Middleware to protect routes
 * Verifies JWT token and adds user to request
 */
exports.protect = async (req, res, next) => {
  try {
    let token;

    // Get token from Authorization header
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
    }

    // Check if token exists
    if (!token) {
      return res.status(401).json({
        status: 'error',
        message: 'Not authenticated. Please log in.'
      });
    }

    try {
      // Verify token
      const decoded = jwt.verify(token, JWT_SECRET);

      // Check if user exists
      const user = await db.get('SELECT id, is_active FROM users WHERE id = ?', [decoded.id]);

      if (!user) {
        return res.status(401).json({
          status: 'error',
          message: 'The user belonging to this token no longer exists'
        });
      }

      if (!user.is_active) {
        return res.status(401).json({
          status: 'error',
          message: 'Your account has been deactivated'
        });
      }

      // Add user to request
      req.user = {
        id: decoded.id,
        roles: decoded.roles || [],
        permissions: decoded.permissions || []
      };

      next();
    } catch (error) {
      // Handle JWT errors
      if (error.name === 'JsonWebTokenError') {
        return res.status(401).json({
          status: 'error',
          message: 'Invalid token. Please log in again.'
        });
      }

      if (error.name === 'TokenExpiredError') {
        return res.status(401).json({
          status: 'error',
          message: 'Your token has expired. Please log in again.'
        });
      }

      throw error;
    }
  } catch (error) {
    next(error);
  }
};

/**
 * Middleware to restrict access based on roles
 * @param {string[]} roles - Array of allowed roles
 */
exports.restrictTo = (...roles) => {
  return (req, res, next) => {
    // Check if user has required role
    if (!req.user.roles.some(role => roles.includes(role))) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to perform this action'
      });
    }

    next();
  };
};

/**
 * Middleware to restrict access based on permissions
 * @param {string} resource - Resource name
 * @param {string} action - Action name
 */
exports.hasPermission = (resource, action) => {
  return (req, res, next) => {
    const requiredPermission = `${resource}:${action}`;

    // Check if user has required permission
    if (!req.user.permissions.includes(requiredPermission)) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to perform this action'
      });
    }

    next();
  };
};