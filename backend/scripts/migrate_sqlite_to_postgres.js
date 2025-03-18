/**
 * Migration Script: SQLite to PostgreSQL
 * 
 * This script migrates data from the SQLite database to PostgreSQL.
 * It extracts data from the SQLite database and inserts it into the PostgreSQL database.
 * 
 * Usage: node migrate_sqlite_to_postgres.js
 */

const sqlite3 = require('sqlite3').verbose();
const { Pool } = require('pg');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');
const bcrypt = require('bcryptjs');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// SQLite database path
const sqliteDbPath = path.resolve(__dirname, '../../hotel_bookings.db');

// Check if SQLite database file exists
if (!fs.existsSync(sqliteDbPath)) {
  console.error(`SQLite database file not found at ${sqliteDbPath}`);
  process.exit(1);
}

// PostgreSQL connection configuration
const pgPool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || 'localhost',
  database: process.env.PGDATABASE || 'hotel_management',
  password: process.env.PGPASSWORD || 'postgres',
  port: process.env.PGPORT || 5432,
});

// Initialize SQLite database connection
const sqliteDb = new sqlite3.Database(sqliteDbPath, (err) => {
  if (err) {
    console.error('SQLite database connection error:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database');
});

// Helper function to run SQLite queries as promises
function sqliteAll(sql, params = []) {
  return new Promise((resolve, reject) => {
    sqliteDb.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

// Helper function to run PostgreSQL queries
async function pgQuery(sql, params = []) {
  const client = await pgPool.connect();
  try {
    const result = await client.query(sql, params);
    return result;
  } finally {
    client.release();
  }
}

// Migrate users table
async function migrateUsers() {
  console.log('Migrating users...');
  
  try {
    // Get users from SQLite
    const users = await sqliteAll('SELECT * FROM users');
    
    if (users.length === 0) {
      console.log('No users to migrate');
      return;
    }
    
    console.log(`Found ${users.length} users to migrate`);
    
    // Insert users into PostgreSQL
    for (const user of users) {
      // Check if user already exists in PostgreSQL
      const existingUser = await pgQuery(
        'SELECT id FROM users WHERE email = $1',
        [user.email]
      );
      
      if (existingUser.rows.length > 0) {
        console.log(`User ${user.email} already exists in PostgreSQL, skipping...`);
        continue;
      }
      
      // Insert user into PostgreSQL
      const result = await pgQuery(
        `INSERT INTO users (
          email, password_hash, first_name, last_name, user_type,
          created_at, last_login, is_active, phone, timezone, locale
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id`,
        [
          user.email,
          user.password_hash,
          user.first_name,
          user.last_name,
          user.user_type,
          user.created_at ? new Date(user.created_at) : new Date(),
          user.last_login ? new Date(user.last_login) : null,
          user.is_active === 1,
          user.phone,
          user.timezone || 'UTC',
          user.locale || 'en'
        ]
      );
      
      console.log(`Migrated user ${user.email} with ID ${result.rows[0].id}`);
      
      // Migrate user roles
      await migrateUserRoles(user.id, result.rows[0].id);
      
      // Migrate user profiles
      if (user.user_type === 'staff') {
        await migrateStaffProfile(user.id, result.rows[0].id);
      } else if (user.user_type === 'guest') {
        await migrateGuestProfile(user.id, result.rows[0].id);
      }
    }
    
    console.log('Users migration completed');
  } catch (error) {
    console.error('Error migrating users:', error);
  }
}

// Migrate user roles
async function migrateUserRoles(sqliteUserId, pgUserId) {
  try {
    // Get user roles from SQLite
    const userRoles = await sqliteAll(
      'SELECT r.name FROM roles r JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = ?',
      [sqliteUserId]
    );
    
    if (userRoles.length === 0) {
      console.log(`No roles found for user ID ${sqliteUserId}`);
      return;
    }
    
    // Insert user roles into PostgreSQL
    for (const role of userRoles) {
      // Get role ID from PostgreSQL
      const pgRole = await pgQuery(
        'SELECT id FROM roles WHERE name = $1',
        [role.name]
      );
      
      if (pgRole.rows.length === 0) {
        console.log(`Role ${role.name} not found in PostgreSQL, skipping...`);
        continue;
      }
      
      // Insert user role into PostgreSQL
      await pgQuery(
        'INSERT INTO user_roles (user_id, role_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
        [pgUserId, pgRole.rows[0].id]
      );
      
      console.log(`Assigned role ${role.name} to user ID ${pgUserId}`);
    }
  } catch (error) {
    console.error(`Error migrating roles for user ID ${sqliteUserId}:`, error);
  }
}

// Migrate staff profiles
async function migrateStaffProfile(sqliteUserId, pgUserId) {
  try {
    // Get staff profile from SQLite
    const staffProfile = await sqliteAll(
      'SELECT * FROM staff_profiles WHERE user_id = ?',
      [sqliteUserId]
    );
    
    if (staffProfile.length === 0) {
      console.log(`No staff profile found for user ID ${sqliteUserId}`);
      return;
    }
    
    // Insert staff profile into PostgreSQL
    await pgQuery(
      `INSERT INTO staff_profiles (
        user_id, role, department, employee_id
      ) VALUES ($1, $2, $3, $4)
      ON CONFLICT (user_id) DO UPDATE SET
        role = EXCLUDED.role,
        department = EXCLUDED.department,
        employee_id = EXCLUDED.employee_id`,
      [
        pgUserId,
        staffProfile[0].role,
        staffProfile[0].department,
        staffProfile[0].employee_id
      ]
    );
    
    console.log(`Migrated staff profile for user ID ${pgUserId}`);
  } catch (error) {
    console.error(`Error migrating staff profile for user ID ${sqliteUserId}:`, error);
  }
}

// Migrate guest profiles
async function migrateGuestProfile(sqliteUserId, pgUserId) {
  try {
    // Get guest profile from SQLite
    const guestProfile = await sqliteAll(
      'SELECT * FROM guest_profiles WHERE user_id = ?',
      [sqliteUserId]
    );
    
    if (guestProfile.length === 0) {
      console.log(`No guest profile found for user ID ${sqliteUserId}`);
      return;
    }
    
    // Insert guest profile into PostgreSQL
    await pgQuery(
      `INSERT INTO guest_profiles (
        user_id, room_number, check_in, check_out, preferences
      ) VALUES ($1, $2, $3, $4, $5)
      ON CONFLICT (user_id) DO UPDATE SET
        room_number = EXCLUDED.room_number,
        check_in = EXCLUDED.check_in,
        check_out = EXCLUDED.check_out,
        preferences = EXCLUDED.preferences`,
      [
        pgUserId,
        guestProfile[0].room_number,
        guestProfile[0].check_in ? new Date(guestProfile[0].check_in) : null,
        guestProfile[0].check_out ? new Date(guestProfile[0].check_out) : null,
        guestProfile[0].preferences ? JSON.parse(guestProfile[0].preferences) : null
      ]
    );
    
    console.log(`Migrated guest profile for user ID ${pgUserId}`);
  } catch (error) {
    console.error(`Error migrating guest profile for user ID ${sqliteUserId}:`, error);
  }
}

// Migrate alerts table
async function migrateAlerts() {
  console.log('Migrating alerts...');
  
  try {
    // Get alerts from SQLite
    const alerts = await sqliteAll('SELECT * FROM alerts');
    
    if (alerts.length === 0) {
      console.log('No alerts to migrate');
      return;
    }
    
    console.log(`Found ${alerts.length} alerts to migrate`);
    
    // Insert alerts into PostgreSQL
    for (const alert of alerts) {
      await pgQuery(
        `INSERT INTO alerts (
          id, type, message, room_number, created_at, is_resolved
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
          type = EXCLUDED.type,
          message = EXCLUDED.message,
          room_number = EXCLUDED.room_number,
          created_at = EXCLUDED.created_at,
          is_resolved = EXCLUDED.is_resolved`,
        [
          alert.id,
          alert.type,
          alert.message,
          alert.room_number,
          alert.created_at ? new Date(alert.created_at) : new Date(),
          alert.is_resolved === 1
        ]
      );
    }
    
    console.log('Alerts migration completed');
  } catch (error) {
    console.error('Error migrating alerts:', error);
  }
}

// Migrate notifications table
async function migrateNotifications() {
  console.log('Migrating notifications...');
  
  try {
    // Get notifications from SQLite
    const notifications = await sqliteAll('SELECT * FROM notifications');
    
    if (notifications.length === 0) {
      console.log('No notifications to migrate');
      return;
    }
    
    console.log(`Found ${notifications.length} notifications to migrate`);
    
    // Insert notifications into PostgreSQL
    for (const notification of notifications) {
      await pgQuery(
        `INSERT INTO notifications (
          id, room_number, message, created_at, is_read
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
          room_number = EXCLUDED.room_number,
          message = EXCLUDED.message,
          created_at = EXCLUDED.created_at,
          is_read = EXCLUDED.is_read`,
        [
          notification.id,
          notification.room_number,
          notification.message,
          notification.created_at ? new Date(notification.created_at) : new Date(),
          notification.is_read === 1
        ]
      );
    }
    
    console.log('Notifications migration completed');
  } catch (error) {
    console.error('Error migrating notifications:', error);
  }
}

// Main migration function
async function migrateData() {
  try {
    console.log('Starting migration from SQLite to PostgreSQL...');
    
    // Migrate users and related data
    await migrateUsers();
    
    // Migrate alerts
    await migrateAlerts();
    
    // Migrate notifications
    await migrateNotifications();
    
    console.log('Migration completed successfully!');
  } catch (error) {
    console.error('Migration error:', error);
  } finally {
    // Close database connections
    sqliteDb.close();
    await pgPool.end();
  }
}

// Run the migration
migrateData();