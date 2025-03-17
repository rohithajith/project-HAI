const bcrypt = require('bcryptjs');
const db = require('../config/database');

/**
 * Get all users
 * Accessible by admin and manager roles
 */
exports.getAllUsers = async (req, res, next) => {
  try {
    // Pagination parameters
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    // Filtering parameters
    const userType = req.query.userType;
    const isActive = req.query.isActive;
    const search = req.query.search;

    // Build query
    let query = `
      SELECT u.id, u.email, u.first_name, u.last_name, u.user_type, 
             u.created_at, u.last_login, u.is_active
      FROM users u
      WHERE 1=1
    `;
    
    const queryParams = [];

    // Add filters
    if (userType) {
      query += ' AND u.user_type = ?';
      queryParams.push(userType);
    }

    if (isActive !== undefined) {
      query += ' AND u.is_active = ?';
      queryParams.push(isActive === 'true' ? 1 : 0);
    }

    if (search) {
      query += ` AND (
        u.email LIKE ? OR 
        u.first_name LIKE ? OR 
        u.last_name LIKE ?
      )`;
      const searchTerm = `%${search}%`;
      queryParams.push(searchTerm, searchTerm, searchTerm);
    }

    // Count total users for pagination
    const countQuery = query.replace('u.id, u.email, u.first_name, u.last_name, u.user_type, u.created_at, u.last_login, u.is_active', 'COUNT(*) as total');
    const countResult = await db.get(countQuery, queryParams);
    const total = countResult.total;

    // Add pagination
    query += ' ORDER BY u.created_at DESC LIMIT ? OFFSET ?';
    queryParams.push(limit, offset);

    // Execute query
    const users = await db.all(query, queryParams);

    // Get roles for each user
    for (const user of users) {
      const roles = await db.all(
        `SELECT r.name
         FROM roles r
         JOIN user_roles ur ON r.id = ur.role_id
         WHERE ur.user_id = ?`,
        [user.id]
      );
      
      user.roles = roles.map(role => role.name);
    }

    res.status(200).json({
      status: 'success',
      data: {
        users,
        pagination: {
          total,
          page,
          limit,
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get user by ID
 * Accessible by admin, manager, or the user themselves
 */
exports.getUserById = async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id);

    // Check if user is requesting their own data or has admin/manager role
    const isSelfRequest = req.user.id === userId;
    const hasAdminAccess = req.user.roles.some(role => ['admin', 'manager'].includes(role));

    if (!isSelfRequest && !hasAdminAccess) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to access this user data'
      });
    }

    // Get user details
    const user = await db.get(
      `SELECT u.id, u.email, u.first_name, u.last_name, u.user_type, 
              u.created_at, u.last_login, u.is_active, u.phone, 
              u.timezone, u.locale
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
      `SELECT r.id, r.name, r.description
       FROM roles r
       JOIN user_roles ur ON r.id = ur.role_id
       WHERE ur.user_id = ?`,
      [userId]
    );

    user.roles = roles;

    // Get profile based on user type
    if (user.user_type === 'staff') {
      const staffProfile = await db.get(
        `SELECT id, role, department, employee_id
         FROM staff_profiles
         WHERE user_id = ?`,
        [userId]
      );
      
      user.profile = staffProfile || null;
    } else if (user.user_type === 'guest') {
      const guestProfile = await db.get(
        `SELECT id, room_number, check_in, check_out, preferences
         FROM guest_profiles
         WHERE user_id = ?`,
        [userId]
      );
      
      if (guestProfile && guestProfile.preferences) {
        try {
          guestProfile.preferences = JSON.parse(guestProfile.preferences);
        } catch (e) {
          console.error('Error parsing preferences JSON:', e);
        }
      }
      
      user.profile = guestProfile || null;
    }

    res.status(200).json({
      status: 'success',
      data: {
        user
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Create a new user
 * Accessible by admin role
 */
exports.createUser = async (req, res, next) => {
  try {
    const {
      email,
      password,
      firstName,
      lastName,
      userType,
      phone,
      timezone,
      locale,
      isActive,
      roles,
      profile
    } = req.body;

    // Validate required fields
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
      `INSERT INTO users (
        email, password_hash, first_name, last_name, user_type,
        phone, timezone, locale, is_active
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        email,
        passwordHash,
        firstName,
        lastName,
        userType,
        phone || null,
        timezone || 'UTC',
        locale || 'en',
        isActive === false ? 0 : 1
      ]
    );

    const userId = result.lastID;

    // Assign roles
    if (roles && Array.isArray(roles) && roles.length > 0) {
      for (const roleName of roles) {
        const role = await db.get('SELECT id FROM roles WHERE name = ?', [roleName]);
        if (role) {
          await db.run(
            'INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)',
            [userId, role.id]
          );
        }
      }
    } else {
      // Assign default role based on user type
      const defaultRole = await db.get('SELECT id FROM roles WHERE name = ?', [userType]);
      if (defaultRole) {
        await db.run(
          'INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)',
          [userId, defaultRole.id]
        );
      }
    }

    // Create profile based on user type
    if (userType === 'staff' && profile) {
      await db.run(
        `INSERT INTO staff_profiles (
          user_id, role, department, employee_id
        ) VALUES (?, ?, ?, ?)`,
        [
          userId,
          profile.role || 'general',
          profile.department || null,
          profile.employeeId || null
        ]
      );
    } else if (userType === 'guest' && profile) {
      let preferences = null;
      if (profile.preferences) {
        preferences = typeof profile.preferences === 'string'
          ? profile.preferences
          : JSON.stringify(profile.preferences);
      }

      await db.run(
        `INSERT INTO guest_profiles (
          user_id, room_number, check_in, check_out, preferences
        ) VALUES (?, ?, ?, ?, ?)`,
        [
          userId,
          profile.roomNumber || null,
          profile.checkIn || null,
          profile.checkOut || null,
          preferences
        ]
      );
    }

    // Log user creation
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        req.user.id,
        'create',
        'users',
        JSON.stringify({ userId, email, userType }),
        req.ip
      ]
    );

    res.status(201).json({
      status: 'success',
      message: 'User created successfully',
      data: {
        userId
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Update user
 * Accessible by admin, manager, or the user themselves (with restrictions)
 */
exports.updateUser = async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id);
    const {
      firstName,
      lastName,
      phone,
      timezone,
      locale,
      isActive,
      roles,
      profile
    } = req.body;

    // Check if user exists
    const user = await db.get('SELECT user_type, is_active FROM users WHERE id = ?', [userId]);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Check permissions
    const isSelfUpdate = req.user.id === userId;
    const isAdmin = req.user.roles.includes('admin');
    const isManager = req.user.roles.includes('manager');

    // Only admins can change active status or roles
    if ((isActive !== undefined || roles) && !isAdmin) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to update user status or roles'
      });
    }

    // Users can only update their own profile unless they are admin/manager
    if (!isSelfUpdate && !isAdmin && !isManager) {
      return res.status(403).json({
        status: 'error',
        message: 'You do not have permission to update this user'
      });
    }

    // Build update query
    const updateFields = [];
    const updateParams = [];

    if (firstName) {
      updateFields.push('first_name = ?');
      updateParams.push(firstName);
    }

    if (lastName) {
      updateFields.push('last_name = ?');
      updateParams.push(lastName);
    }

    if (phone !== undefined) {
      updateFields.push('phone = ?');
      updateParams.push(phone);
    }

    if (timezone) {
      updateFields.push('timezone = ?');
      updateParams.push(timezone);
    }

    if (locale) {
      updateFields.push('locale = ?');
      updateParams.push(locale);
    }

    if (isActive !== undefined && isAdmin) {
      updateFields.push('is_active = ?');
      updateParams.push(isActive ? 1 : 0);
    }

    // Only update if there are fields to update
    if (updateFields.length > 0) {
      updateParams.push(userId);
      
      await db.run(
        `UPDATE users SET ${updateFields.join(', ')} WHERE id = ?`,
        updateParams
      );
    }

    // Update roles if provided and user is admin
    if (roles && Array.isArray(roles) && isAdmin) {
      // Remove existing roles
      await db.run('DELETE FROM user_roles WHERE user_id = ?', [userId]);

      // Add new roles
      for (const roleName of roles) {
        const role = await db.get('SELECT id FROM roles WHERE name = ?', [roleName]);
        if (role) {
          await db.run(
            'INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)',
            [userId, role.id]
          );
        }
      }
    }

    // Update profile if provided
    if (profile) {
      if (user.user_type === 'staff') {
        // Check if profile exists
        const staffProfile = await db.get(
          'SELECT id FROM staff_profiles WHERE user_id = ?',
          [userId]
        );

        if (staffProfile) {
          // Update existing profile
          const updateFields = [];
          const updateParams = [];

          if (profile.role) {
            updateFields.push('role = ?');
            updateParams.push(profile.role);
          }

          if (profile.department !== undefined) {
            updateFields.push('department = ?');
            updateParams.push(profile.department);
          }

          if (profile.employeeId !== undefined) {
            updateFields.push('employee_id = ?');
            updateParams.push(profile.employeeId);
          }

          if (updateFields.length > 0) {
            updateParams.push(userId);
            
            await db.run(
              `UPDATE staff_profiles SET ${updateFields.join(', ')} WHERE user_id = ?`,
              updateParams
            );
          }
        } else {
          // Create new profile
          await db.run(
            `INSERT INTO staff_profiles (user_id, role, department, employee_id)
             VALUES (?, ?, ?, ?)`,
            [
              userId,
              profile.role || 'general',
              profile.department || null,
              profile.employeeId || null
            ]
          );
        }
      } else if (user.user_type === 'guest') {
        // Check if profile exists
        const guestProfile = await db.get(
          'SELECT id FROM guest_profiles WHERE user_id = ?',
          [userId]
        );

        let preferences = null;
        if (profile.preferences) {
          preferences = typeof profile.preferences === 'string'
            ? profile.preferences
            : JSON.stringify(profile.preferences);
        }

        if (guestProfile) {
          // Update existing profile
          const updateFields = [];
          const updateParams = [];

          if (profile.roomNumber !== undefined) {
            updateFields.push('room_number = ?');
            updateParams.push(profile.roomNumber);
          }

          if (profile.checkIn !== undefined) {
            updateFields.push('check_in = ?');
            updateParams.push(profile.checkIn);
          }

          if (profile.checkOut !== undefined) {
            updateFields.push('check_out = ?');
            updateParams.push(profile.checkOut);
          }

          if (profile.preferences !== undefined) {
            updateFields.push('preferences = ?');
            updateParams.push(preferences);
          }

          if (updateFields.length > 0) {
            updateParams.push(userId);
            
            await db.run(
              `UPDATE guest_profiles SET ${updateFields.join(', ')} WHERE user_id = ?`,
              updateParams
            );
          }
        } else {
          // Create new profile
          await db.run(
            `INSERT INTO guest_profiles (user_id, room_number, check_in, check_out, preferences)
             VALUES (?, ?, ?, ?, ?)`,
            [
              userId,
              profile.roomNumber || null,
              profile.checkIn || null,
              profile.checkOut || null,
              preferences
            ]
          );
        }
      }
    }

    // Log user update
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        req.user.id,
        'update',
        'users',
        JSON.stringify({ userId, updatedBy: req.user.id }),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'User updated successfully'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Delete user
 * Accessible by admin role only
 */
exports.deleteUser = async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id);

    // Check if user exists
    const user = await db.get('SELECT id FROM users WHERE id = ?', [userId]);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Prevent self-deletion
    if (userId === req.user.id) {
      return res.status(400).json({
        status: 'error',
        message: 'You cannot delete your own account'
      });
    }

    // Log user deletion before deleting the user
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        req.user.id,
        'delete',
        'users',
        JSON.stringify({ deletedUserId: userId }),
        req.ip
      ]
    );

    // Delete user (cascade will handle related records)
    await db.run('DELETE FROM users WHERE id = ?', [userId]);

    res.status(200).json({
      status: 'success',
      message: 'User deleted successfully'
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Get user roles
 * Accessible by admin role
 */
exports.getUserRoles = async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id);

    // Check if user exists
    const user = await db.get('SELECT id FROM users WHERE id = ?', [userId]);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Get user roles
    const roles = await db.all(
      `SELECT r.id, r.name, r.description
       FROM roles r
       JOIN user_roles ur ON r.id = ur.role_id
       WHERE ur.user_id = ?`,
      [userId]
    );

    res.status(200).json({
      status: 'success',
      data: {
        roles
      }
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Update user roles
 * Accessible by admin role
 */
exports.updateUserRoles = async (req, res, next) => {
  try {
    const userId = parseInt(req.params.id);
    const { roles } = req.body;

    if (!roles || !Array.isArray(roles)) {
      return res.status(400).json({
        status: 'error',
        message: 'Please provide an array of role names'
      });
    }

    // Check if user exists
    const user = await db.get('SELECT id FROM users WHERE id = ?', [userId]);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: 'User not found'
      });
    }

    // Remove existing roles
    await db.run('DELETE FROM user_roles WHERE user_id = ?', [userId]);

    // Add new roles
    for (const roleName of roles) {
      const role = await db.get('SELECT id FROM roles WHERE name = ?', [roleName]);
      if (role) {
        await db.run(
          'INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)',
          [userId, role.id]
        );
      }
    }

    // Log role update
    await db.run(
      'INSERT INTO audit_logs (user_id, action, resource, details, ip_address) VALUES (?, ?, ?, ?, ?)',
      [
        req.user.id,
        'update_roles',
        'users',
        JSON.stringify({ userId, roles }),
        req.ip
      ]
    );

    res.status(200).json({
      status: 'success',
      message: 'User roles updated successfully'
    });
  } catch (error) {
    next(error);
  }
};