/**
 * Seed script to create dummy users for testing
 * 
 * Run with: node seedUsers.js
 */

const bcrypt = require('bcryptjs');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Database path
const dbPath = path.resolve(__dirname, '../../hotel_bookings.db');

// Check if database file exists
if (!fs.existsSync(dbPath)) {
  console.error(`Database file not found at ${dbPath}`);
  process.exit(1);
}

// Initialize database connection
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database');
});

// Helper function to run SQL as a Promise
function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
      if (err) reject(err);
      else resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
}

// Helper function to get a single row as a Promise
function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

// Helper function to get all rows as a Promise
function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// Dummy users to create
const users = [
  {
    email: 'admin@hotel.com',
    password: 'Admin123!',
    firstName: 'Admin',
    lastName: 'User',
    userType: 'admin',
    phone: '+1234567890',
    roles: ['admin']
  },
  {
    email: 'manager@hotel.com',
    password: 'Manager123!',
    firstName: 'Manager',
    lastName: 'User',
    userType: 'staff',
    phone: '+1234567891',
    roles: ['manager'],
    profile: {
      role: 'manager',
      department: 'Management',
      employeeId: 'M001'
    }
  },
  {
    email: 'staff@hotel.com',
    password: 'Staff123!',
    firstName: 'Staff',
    lastName: 'User',
    userType: 'staff',
    phone: '+1234567892',
    roles: ['staff'],
    profile: {
      role: 'receptionist',
      department: 'Front Desk',
      employeeId: 'S001'
    }
  },
  {
    email: 'guest1@example.com',
    password: 'Guest123!',
    firstName: 'Guest',
    lastName: 'One',
    userType: 'guest',
    phone: '+1234567893',
    roles: ['guest'],
    profile: {
      roomNumber: '101',
      checkIn: '2025-03-15',
      checkOut: '2025-03-20',
      preferences: JSON.stringify({
        temperature: '72F',
        cleaning: 'morning',
        pillows: 'firm',
        wakeupCall: '7:00 AM'
      })
    }
  },
  {
    email: 'guest2@example.com',
    password: 'Guest123!',
    firstName: 'Guest',
    lastName: 'Two',
    userType: 'guest',
    phone: '+1234567894',
    roles: ['guest'],
    profile: {
      roomNumber: '202',
      checkIn: '2025-03-16',
      checkOut: '2025-03-22',
      preferences: JSON.stringify({
        temperature: '68F',
        cleaning: 'afternoon',
        pillows: 'soft',
        wakeupCall: '8:30 AM'
      })
    }
  }
];

// Main function to seed users
async function seedUsers() {
  try {
    console.log('Starting to seed users...');
    
    for (const userData of users) {
      // Check if user already exists
      const existingUser = await get('SELECT id FROM users WHERE email = ?', [userData.email]);
      
      if (existingUser) {
        console.log(`User ${userData.email} already exists, skipping...`);
        continue;
      }
      
      // Hash password
      const salt = await bcrypt.genSalt(10);
      const passwordHash = await bcrypt.hash(userData.password, salt);
      
      // Create user
      console.log(`Creating user: ${userData.email}`);
      const result = await run(
        `INSERT INTO users (
          email, password_hash, first_name, last_name, user_type,
          phone, created_at, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 1)`,
        [
          userData.email,
          passwordHash,
          userData.firstName,
          userData.lastName,
          userData.userType,
          userData.phone
        ]
      );
      
      const userId = result.lastID;
      
      // Assign roles
      for (const roleName of userData.roles) {
        const role = await get('SELECT id FROM roles WHERE name = ?', [roleName]);
        
        if (role) {
          await run(
            'INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)',
            [userId, role.id]
          );
          console.log(`Assigned role ${roleName} to user ${userData.email}`);
        } else {
          console.warn(`Role ${roleName} not found, skipping...`);
        }
      }
      
      // Create profile based on user type
      if (userData.userType === 'staff' && userData.profile) {
        await run(
          `INSERT INTO staff_profiles (
            user_id, role, department, employee_id
          ) VALUES (?, ?, ?, ?)`,
          [
            userId,
            userData.profile.role,
            userData.profile.department,
            userData.profile.employeeId
          ]
        );
        console.log(`Created staff profile for user ${userData.email}`);
      } else if (userData.userType === 'guest' && userData.profile) {
        await run(
          `INSERT INTO guest_profiles (
            user_id, room_number, check_in, check_out, preferences
          ) VALUES (?, ?, ?, ?, ?)`,
          [
            userId,
            userData.profile.roomNumber,
            userData.profile.checkIn,
            userData.profile.checkOut,
            userData.profile.preferences
          ]
        );
        console.log(`Created guest profile for user ${userData.email}`);
      }
      
      console.log(`User ${userData.email} created successfully with ID ${userId}`);
    }
    
    console.log('User seeding completed successfully!');
  } catch (error) {
    console.error('Error seeding users:', error);
  } finally {
    // Close database connection
    db.close((err) => {
      if (err) {
        console.error('Error closing database connection:', err.message);
      } else {
        console.log('Database connection closed');
      }
    });
  }
}

// Run the seed function
seedUsers();