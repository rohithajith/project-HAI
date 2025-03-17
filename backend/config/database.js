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
let db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database');
  
  // Initialize tables after connection
  initializeTables();
});

// Create tables if they don't exist
function initializeTables() {
  // Create users table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      user_type TEXT NOT NULL, -- 'admin', 'staff', 'guest'
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      last_login DATETIME,
      is_active BOOLEAN DEFAULT 1,
      phone TEXT,
      timezone TEXT DEFAULT 'UTC',
      locale TEXT DEFAULT 'en'
    )
  `, (err) => {
    if (err) {
      console.error('Error creating users table:', err.message);
    }
  });

  // Create roles table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS roles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      description TEXT
    )
  `, (err) => {
    if (err) {
      console.error('Error creating roles table:', err.message);
    }
  });

  // Create permissions table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS permissions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      resource TEXT NOT NULL,
      action TEXT NOT NULL,
      description TEXT,
      UNIQUE(resource, action)
    )
  `, (err) => {
    if (err) {
      console.error('Error creating permissions table:', err.message);
    }
  });

  // Create user_roles table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS user_roles (
      user_id INTEGER NOT NULL,
      role_id INTEGER NOT NULL,
      PRIMARY KEY (user_id, role_id),
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
      FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating user_roles table:', err.message);
    }
  });

  // Create role_permissions table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS role_permissions (
      role_id INTEGER NOT NULL,
      permission_id INTEGER NOT NULL,
      PRIMARY KEY (role_id, permission_id),
      FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
      FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating role_permissions table:', err.message);
    }
  });

  // Create refresh_tokens table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS refresh_tokens (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      token TEXT UNIQUE NOT NULL,
      expires_at DATETIME NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      revoked BOOLEAN DEFAULT 0,
      device_info TEXT,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating refresh_tokens table:', err.message);
    }
  });

  // Create staff_profiles table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS staff_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER UNIQUE NOT NULL,
      role TEXT NOT NULL,
      department TEXT,
      employee_id TEXT UNIQUE,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating staff_profiles table:', err.message);
    }
  });

  // Create guest_profiles table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS guest_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER UNIQUE NOT NULL,
      room_number TEXT,
      check_in DATETIME,
      check_out DATETIME,
      preferences TEXT, -- JSON string
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
  `, (err) => {
    if (err) {
      console.error('Error creating guest_profiles table:', err.message);
    }
  });

  // Create alerts table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS alerts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL,
      message TEXT,
      room_number TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      is_resolved BOOLEAN DEFAULT 0
    )
  `, (err) => {
    if (err) {
      console.error('Error creating alerts table:', err.message);
    }
  });

  // Create notifications table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS notifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      room_number TEXT NOT NULL,
      message TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      is_read BOOLEAN DEFAULT 0
    )
  `, (err) => {
    if (err) {
      console.error('Error creating notifications table:', err.message);
    } else {
      console.log('Database tables initialized');
    }
  });

  // Create audit_logs table if it doesn't exist
  db.run(`
    CREATE TABLE IF NOT EXISTS audit_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      action TEXT NOT NULL,
      resource TEXT NOT NULL,
      details TEXT, -- JSON string
      ip_address TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    )
  `, (err) => {
    if (err) {
      console.error('Error creating audit_logs table:', err.message);
    }
  });

  // Insert default roles if they don't exist
  insertDefaultRolesAndPermissions();
}

// Insert default roles and permissions
function insertDefaultRolesAndPermissions() {
  // Insert default roles
  const roles = [
    { name: 'admin', description: 'Administrator with full access' },
    { name: 'manager', description: 'Hotel manager with access to most features' },
    { name: 'staff', description: 'Hotel staff with limited access' },
    { name: 'guest', description: 'Hotel guest with access to guest features only' }
  ];

  roles.forEach(role => {
    db.get('SELECT id FROM roles WHERE name = ?', [role.name], (err, row) => {
      if (err) {
        console.error(`Error checking for role ${role.name}:`, err.message);
        return;
      }
      
      if (!row) {
        db.run('INSERT INTO roles (name, description) VALUES (?, ?)',
          [role.name, role.description],
          function(err) {
            if (err) {
              console.error(`Error inserting role ${role.name}:`, err.message);
            } else {
              console.log(`Role ${role.name} created with ID ${this.lastID}`);
              
              // Insert permissions for this role
              if (role.name === 'admin') {
                insertAdminPermissions(this.lastID);
              } else if (role.name === 'manager') {
                insertManagerPermissions(this.lastID);
              } else if (role.name === 'staff') {
                insertStaffPermissions(this.lastID);
              } else if (role.name === 'guest') {
                insertGuestPermissions(this.lastID);
              }
            }
          }
        );
      }
    });
  });
}

// Insert admin permissions
function insertAdminPermissions(roleId) {
  const permissions = [
    { resource: 'users', action: 'create' },
    { resource: 'users', action: 'read' },
    { resource: 'users', action: 'update' },
    { resource: 'users', action: 'delete' },
    { resource: 'roles', action: 'create' },
    { resource: 'roles', action: 'read' },
    { resource: 'roles', action: 'update' },
    { resource: 'roles', action: 'delete' },
    { resource: 'bookings', action: 'create' },
    { resource: 'bookings', action: 'read' },
    { resource: 'bookings', action: 'update' },
    { resource: 'bookings', action: 'delete' },
    { resource: 'alerts', action: 'create' },
    { resource: 'alerts', action: 'read' },
    { resource: 'alerts', action: 'update' },
    { resource: 'alerts', action: 'delete' },
    { resource: 'notifications', action: 'create' },
    { resource: 'notifications', action: 'read' },
    { resource: 'notifications', action: 'update' },
    { resource: 'notifications', action: 'delete' }
  ];
  
  insertPermissionsForRole(permissions, roleId);
}

// Insert manager permissions
function insertManagerPermissions(roleId) {
  const permissions = [
    { resource: 'users', action: 'read' },
    { resource: 'users', action: 'update' },
    { resource: 'bookings', action: 'create' },
    { resource: 'bookings', action: 'read' },
    { resource: 'bookings', action: 'update' },
    { resource: 'alerts', action: 'create' },
    { resource: 'alerts', action: 'read' },
    { resource: 'alerts', action: 'update' },
    { resource: 'notifications', action: 'create' },
    { resource: 'notifications', action: 'read' },
    { resource: 'notifications', action: 'update' }
  ];
  
  insertPermissionsForRole(permissions, roleId);
}

// Insert staff permissions
function insertStaffPermissions(roleId) {
  const permissions = [
    { resource: 'bookings', action: 'read' },
    { resource: 'bookings', action: 'update' },
    { resource: 'alerts', action: 'read' },
    { resource: 'alerts', action: 'update' },
    { resource: 'notifications', action: 'create' },
    { resource: 'notifications', action: 'read' }
  ];
  
  insertPermissionsForRole(permissions, roleId);
}

// Insert guest permissions
function insertGuestPermissions(roleId) {
  const permissions = [
    { resource: 'bookings', action: 'read' },
    { resource: 'alerts', action: 'create' },
    { resource: 'alerts', action: 'read' },
    { resource: 'notifications', action: 'read' }
  ];
  
  insertPermissionsForRole(permissions, roleId);
}

// Helper function to insert permissions for a role
function insertPermissionsForRole(permissions, roleId) {
  permissions.forEach(perm => {
    // First, insert the permission if it doesn't exist
    db.get('SELECT id FROM permissions WHERE resource = ? AND action = ?',
      [perm.resource, perm.action],
      (err, row) => {
        if (err) {
          console.error(`Error checking for permission ${perm.resource}:${perm.action}:`, err.message);
          return;
        }
        
        let permissionId;
        
        if (!row) {
          db.run('INSERT INTO permissions (resource, action, description) VALUES (?, ?, ?)',
            [perm.resource, perm.action, `${perm.action} ${perm.resource}`],
            function(err) {
              if (err) {
                console.error(`Error inserting permission ${perm.resource}:${perm.action}:`, err.message);
                return;
              }
              
              permissionId = this.lastID;
              assignPermissionToRole(permissionId, roleId);
            }
          );
        } else {
          permissionId = row.id;
          assignPermissionToRole(permissionId, roleId);
        }
      }
    );
  });
}

// Assign a permission to a role
function assignPermissionToRole(permissionId, roleId) {
  db.run('INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES (?, ?)',
    [roleId, permissionId],
    function(err) {
      if (err) {
        console.error(`Error assigning permission ${permissionId} to role ${roleId}:`, err.message);
      }
    }
  );
}

// Helper functions to wrap sqlite3 callbacks in promises
const dbAsync = {
  all: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  },
  
  get: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  },
  
  run: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  },
  
  exec: (sql) => {
    return new Promise((resolve, reject) => {
      db.exec(sql, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }
};

module.exports = dbAsync;