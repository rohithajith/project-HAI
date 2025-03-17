const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const db = require('../config/database');

// Environment variables
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret_key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '1h';
const JWT_REFRESH_EXPIRES_IN = process.env.JWT_REFRESH_EXPIRES_IN || '7d';

/**
 * Register a new user
 */
exports.register = async (req, res, next) => {
  try {
    const { email, password, firstName, lastName, userType, phone } = req.body;

    // Validate input
    if (!email || !password || !firstName || !lastName || !userType) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide all required fields'
      });
    }

    // Check if user already exists
    const existingUser = await db.get('SELECT id FROM users WHERE email = ?', [email]);
    if (existingUser) {
      return res.status(400).json({
        status: 'error',
        message: 'User with this email already exists'
      });
    }

    // Validate user type
    const validUserTypes = ['admin', 'staff', 'guest'];
    if (!validUserTypes.includes(userType)) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid user type'
      });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(password, salt);

    // Create user
    const result = await db.run(
      'INSERT INTO users (email, password_hash, first_name, last_name, user_type, phone) VALUES (?, ?, ?, ?, ?, ?)',
      [email, passwordHash, firstName, lastName, userType, phone || null]
    );

    const userId = result.lastID;

    // Assign default role based on user type
    const role = await db.get('SELECT id FROM roles WHERE name = ?', [userType]);
    if (role) {
      await db.run('INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)', [userId, role.id]);
    }

    // Create profile based on user type
    if (userType === 'staff') {
      await db.run(
        'INSERT INTO staff_profiles (user_id, role, department) VALUES (?, ?, ?)',
        [userId, 'general', 'general']
      );
    } else if (userType === 'guest') {
      await db.run(
        'INSERT INTO guest_profiles (user_id) VALUES (?)',
        [userId]
      );
    }

    // Log the registration
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        userId,
        'register',
        'users',
        JSON.stringify({ email, userType }),
        req.ip
      ]
    );

    // Generate tokens
    const { accessToken, refreshToken } = await generateTokens(userId);

    // Store refresh token
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7); // 7 days from now

    await db.run(
      'INSERT INTO refresh_tokens (user_id, token, expires_at, device_info) VALUES (?, ?, ?, ?)',
      [
        userId,
        refreshToken,
        expiresAt.toISOString(),
        req.headers['user-agent'] || null
      ]
    );

    res.status(201).json({
      status: 'success',
      message: 'User registered successfully',
      data: {
        user: {
          id: userId,
          email,
          firstName,
          lastName,
          userType
        },
        accessToken,
        refreshToken
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Login user
 */
exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body;

    // Validate input
    if (!email || !password) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide email and password'
      });
    }

    // Get user
    const user = await db.get(
      `SELECT u.id, u.email, u.password_hash, u.first_name, u.last_name, u.user_type, u.is_active
       FROM users u
       WHERE u.email = ?`,
      [email]
    );

    // Check if user exists
    if (!user) {
      return res.status(401).json({
        status: 'error',
        message: 'Invalid credentials'
      });
    }

    // Check if user is active
    if (!user.is_active) {
      return res.status(401).json({
        status: 'error',
        message: 'Your account has been deactivated. Please contact support.'
      });
    }

    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
      // Log failed login attempt
      await db.run(
        'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
        [
          user.id,
          'login_failed',
          'auth',
          JSON.stringify({ reason: 'invalid_password' }),
          req.ip
        ]
      );

      return res.status(401).json({
        status: 'error',
        message: 'Invalid credentials'
      });
    }

    // Generate tokens
    const { accessToken, refreshToken } = await generateTokens(user.id);

    // Store refresh token
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7); // 7 days from now

    await db.run(
      'INSERT INTO refresh_tokens (user_id, token, expires_at, device_info) VALUES (?, ?, ?, ?)',
      [
        user.id,
        refreshToken,
        expiresAt.toISOString(),
        req.headers['user-agent'] || null
      ]
    );

    // Update last login
    await db.run(
      'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
      [user.id]
    );

    // Log successful login
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        user.id,
        'login',
        'auth',
        JSON.stringify({ method: 'password' }),
        req.ip
      ]
    );

    // Get user roles and permissions
    const userRoles = await db.all(
      `SELECT r.name
       FROM roles r
       JOIN user_roles ur ON r.id = ur.role_id
       WHERE ur.user_id = ?`,
      [user.id]
    );

    const userPermissions = await db.all(
      `SELECT DISTINCT p.resource, p.action
       FROM permissions p
       JOIN role_permissions rp ON p.id = rp.permission_id
       JOIN user_roles ur ON rp.role_id = ur.role_id
       WHERE ur.user_id = ?`,
      [user.id]
    );

    res.status(200).json({
      status: 'success',
      message: 'Login successful',
      data: {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          userType: user.user_type,
          roles: userRoles.map(role => role.name),
          permissions: userPermissions.map(p => `${p.resource}:${p.action}`)
        },
        accessToken,
        refreshToken
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Refresh token
 */
exports.refreshToken = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        status: 'error',
        message: 'Refresh token is required'
      });
    }

    // Check if refresh token exists and is valid
    const tokenRecord = await db.get(
      `SELECT rt.id, rt.user_id, rt.expires_at, rt.revoked
       FROM refresh_tokens rt
       WHERE rt.token = ?`,
      [refreshToken]
    );

    if (!tokenRecord) {
      return res.status(401).json({
        status: 'error',
        message: 'Invalid refresh token'
      });
    }

    // Check if token is expired
    const now = new Date();
    const expiresAt = new Date(tokenRecord.expires_at);
    if (now > expiresAt || tokenRecord.revoked) {
      return res.status(401).json({
        status: 'error',
        message: 'Refresh token expired or revoked'
      });
    }

    // Check if user exists and is active
    const user = await db.get(
      'SELECT id, is_active FROM users WHERE id = ?',
      [tokenRecord.user_id]
    );

    if (!user || !user.is_active) {
      return res.status(401).json({
        status: 'error',
        message: 'User not found or inactive'
      });
    }

    // Generate new tokens
    const tokens = await generateTokens(user.id);

    // Revoke old refresh token
    await db.run(
      'UPDATE refresh_tokens SET revoked = 1 WHERE id = ?',
      [tokenRecord.id]
    );

    // Store new refresh token
    const newExpiresAt = new Date();
    newExpiresAt.setDate(newExpiresAt.getDate() + 7); // 7 days from now

    await db.run(
      'INSERT INTO refresh_tokens (user_id, token, expires_at, device_info) VALUES (?, ?, ?, ?)',
      [
        user.id,
        tokens.refreshToken,
        newExpiresAt.toISOString(),
        req.headers['user-agent'] || null
      ]
    );

    // Log token refresh
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        user.id,
        'token_refresh',
        'auth',
        JSON.stringify({ old_token_id: tokenRecord.id }),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'Token refreshed successfully',
      data: {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Logout user
 */
exports.logout = async (req, res, next) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        status: 'error',
        message: 'Refresh token is required'
      });
    }

    // Revoke refresh token
    const result = await db.run(
      'UPDATE refresh_tokens SET revoked = 1 WHERE token = ?',
      [refreshToken]
    );

    if (result.changes === 0) {
      return res.status(404).json({
        status: 'error',
        message: 'Token not found'
      });
    }

    // Get user ID for audit log
    const tokenRecord = await db.get(
      'SELECT user_id FROM refresh_tokens WHERE token = ?',
      [refreshToken]
    );

    if (tokenRecord) {
      // Log logout
      await db.run(
        'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
        [
          tokenRecord.user_id,
          'logout',
          'auth',
          JSON.stringify({}),
          req.ip
        ]
      );
    }

    res.status(200).json({
      status: 'success',
      message: 'Logged out successfully'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get current user
 */
exports.getCurrentUser = async (req, res, next) => {
  try {
    const userId = req.user.id;

    // Get user details
    const user = await db.get(
      `SELECT u.id, u.email, u.first_name, u.last_name, u.user_type, u.is_active, 
              u.created_at, u.last_login, u.phone, u.timezone, u.locale
       FROM users u
       WHERE u.id = ?`,
      [userId]
    );

    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Get user roles
    const roles = await db.all(
      `SELECT r.name
       FROM roles r
       JOIN user_roles ur ON r.id = ur.role_id
       WHERE ur.user_id = ?`,
      [userId]
    );

    // Get user permissions
    const permissions = await db.all(
      `SELECT DISTINCT p.resource, p.action
       FROM permissions p
       JOIN role_permissions rp ON p.id = rp.permission_id
       JOIN user_roles ur ON rp.role_id = ur.role_id
       WHERE ur.user_id = ?`,
      [userId]
    );

    // Get profile based on user type
    let profile = null;
    if (user.user_type === 'staff') {
      profile = await db.get(
        'SELECT role, department, employee_id FROM staff_profiles WHERE user_id = ?',
        [userId]
      );
    } else if (user.user_type === 'guest') {
      profile = await db.get(
        'SELECT room_number, check_in, check_out, preferences FROM guest_profiles WHERE user_id = ?',
        [userId]
      );
      
      // Parse preferences JSON if it exists
      if (profile && profile.preferences) {
        try {
          profile.preferences = JSON.parse(profile.preferences);
        } catch (e) {
          console.error('Error parsing preferences JSON:', e);
        }
      }
    }

    res.status(200).json({
      status: 'success',
      data: {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          userType: user.user_type,
          isActive: user.is_active,
          createdAt: user.created_at,
          lastLogin: user.last_login,
          phone: user.phone,
          timezone: user.timezone,
          locale: user.locale,
          roles: roles.map(role => role.name),
          permissions: permissions.map(p => `${p.resource}:${p.action}`),
          profile
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Change password
 */
exports.changePassword = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { currentPassword, newPassword } = req.body;

    // Validate input
    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide current and new password'
      });
    }

    // Get user
    const user = await db.get(
      'SELECT password_hash FROM users WHERE id = ?',
      [userId]
    );

    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Verify current password
    const isPasswordValid = await bcrypt.compare(currentPassword, user.password_hash);
    if (!isPasswordValid) {
      return res.status(401).json({
        status: 'error',
        message: 'Current password is incorrect'
      });
    }

    // Hash new password
    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(newPassword, salt);

    // Update password
    await db.run(
      'UPDATE users SET password_hash = ? WHERE id = ?',
      [passwordHash, userId]
    );

    // Revoke all refresh tokens
    await db.run(
      'UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?',
      [userId]
    );

    // Log password change
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        userId,
        'password_change',
        'users',
        JSON.stringify({}),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'Password changed successfully'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Request password reset
 */
exports.requestPasswordReset = async (req, res, next) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide an email address'
      });
    }

    // Check if user exists
    const user = await db.get(
      'SELECT id, email FROM users WHERE email = ?',
      [email]
    );

    if (!user) {
      // For security reasons, don't reveal that the user doesn't exist
      return res.status(200).json({
        status: 'success',
        message: 'If your email is registered, you will receive a password reset link'
      });
    }

    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetTokenHash = crypto.createHash('sha256').update(resetToken).digest('hex');

    // Set token expiry (1 hour)
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 1);

    // Store reset token
    await db.run(
      `INSERT INTO password_reset_tokens (user_id, token, expires_at)
       VALUES (?, ?, ?)`,
      [user.id, resetTokenHash, expiresAt.toISOString()]
    );

    // In a real application, send an email with the reset link
    // For this example, we'll just return the token
    console.log(`Password reset token for ${email}: ${resetToken}`);

    // Log password reset request
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        user.id,
        'password_reset_request',
        'users',
        JSON.stringify({}),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'If your email is registered, you will receive a password reset link',
      // In a real application, don't return the token
      // For testing purposes only:
      data: {
        resetToken
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Reset password
 */
exports.resetPassword = async (req, res, next) => {
  try {
    const { token, newPassword } = req.body;

    if (!token || !newPassword) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide token and new password'
      });
    }

    // Hash the token to compare with stored hash
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

    // Get token record
    const tokenRecord = await db.get(
      `SELECT id, user_id, expires_at, used
       FROM password_reset_tokens
       WHERE token = ?`,
      [tokenHash]
    );

    if (!tokenRecord) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid or expired token'
      });
    }

    // Check if token is expired or used
    const now = new Date();
    const expiresAt = new Date(tokenRecord.expires_at);
    if (now > expiresAt || tokenRecord.used) {
      return res.status(400).json({
        status: 'error',
        message: 'Token is expired or has already been used'
      });
    }

    // Hash new password
    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(newPassword, salt);

    // Update password
    await db.run(
      'UPDATE users SET password_hash = ? WHERE id = ?',
      [passwordHash, tokenRecord.user_id]
    );

    // Mark token as used
    await db.run(
      'UPDATE password_reset_tokens SET used = 1 WHERE id = ?',
      [tokenRecord.id]
    );

    // Revoke all refresh tokens
    await db.run(
      'UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?',
      [tokenRecord.user_id]
    );

    // Log password reset
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        tokenRecord.user_id,
        'password_reset',
        'users',
        JSON.stringify({}),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'Password reset successful'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Helper function to generate JWT tokens
 */
async function generateTokens(userId) {
  // Get user roles and permissions
  const userRoles = await db.all(
    `SELECT r.name
     FROM roles r
     JOIN user_roles ur ON r.id = ur.role_id
     WHERE ur.user_id = ?`,
    [userId]
  );

  const userPermissions = await db.all(
    `SELECT DISTINCT p.resource, p.action
     FROM permissions p
     JOIN role_permissions rp ON p.id = rp.permission_id
     JOIN user_roles ur ON rp.role_id = ur.role_id
     WHERE ur.user_id = ?`,
    [userId]
  );

  // Create token payload
  const payload = {
    id: userId,
    roles: userRoles.map(role => role.name),
    permissions: userPermissions.map(p => `${p.resource}:${p.action}`)
  };

  // Generate access token
  const accessToken = jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN
  });

  // Generate refresh token
  const refreshToken = crypto.randomBytes(40).toString('hex');

  return {
    accessToken,
    refreshToken
  };
}