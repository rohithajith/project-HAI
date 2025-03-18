/**
 * PostgreSQL Database Initialization Script
 * 
 * This script creates the necessary tables for the hotel management system
 * including user authentication tables and conversation history tables.
 * 
 * Usage: node init_postgres_db.js
 */

const { Pool } = require('pg');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment variables
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// PostgreSQL connection configuration
const pool = new Pool({
  user: process.env.PGUSER || 'postgres',
  host: process.env.PGHOST || 'localhost',
  database: process.env.PGDATABASE || 'hotel_management',
  password: process.env.PGPASSWORD || 'postgres',
  port: process.env.PGPORT || 5432,
});

// SQL statements to create tables
const createAuthTables = `
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    user_type VARCHAR(50) NOT NULL, -- 'admin', 'staff', 'guest'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en'
);

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    UNIQUE(resource, action)
);

-- User roles table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Role permissions table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Refresh tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    device_info TEXT
);

-- Password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used BOOLEAN DEFAULT FALSE
);

-- User profiles tables
CREATE TABLE IF NOT EXISTS staff_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(100),
    employee_id VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS guest_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    room_number VARCHAR(50),
    check_in TIMESTAMP WITH TIME ZONE,
    check_out TIMESTAMP WITH TIME ZONE,
    preferences JSONB
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    details JSONB,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
`;

const createConversationTables = `
-- Data consent table
CREATE TABLE IF NOT EXISTS data_consent (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    service_improvement BOOLEAN DEFAULT FALSE,
    model_training BOOLEAN DEFAULT FALSE,
    analytics BOOLEAN DEFAULT FALSE,
    marketing BOOLEAN DEFAULT FALSE,
    consent_given_at TIMESTAMP WITH TIME ZONE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation sessions table
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    consent_obtained BOOLEAN DEFAULT FALSE,
    anonymized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    message_index INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- LLM metrics table
CREATE TABLE IF NOT EXISTS llm_metrics (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES conversation_messages(id) ON DELETE CASCADE,
    model_name VARCHAR(100),
    tokens_input INTEGER,
    tokens_output INTEGER,
    latency_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_created_at ON conversation_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_metrics_message_id ON llm_metrics(message_id);
`;

// Default roles and permissions
const insertDefaultRoles = `
INSERT INTO roles (name, description)
VALUES 
    ('admin', 'Administrator with full access'),
    ('manager', 'Hotel manager with access to most features'),
    ('staff', 'Hotel staff with limited access'),
    ('guest', 'Hotel guest with access to guest features only')
ON CONFLICT (name) DO NOTHING;
`;

const insertDefaultPermissions = `
-- Insert default permissions
INSERT INTO permissions (resource, action, description)
VALUES 
    ('users', 'create', 'Create users'),
    ('users', 'read', 'Read user data'),
    ('users', 'update', 'Update user data'),
    ('users', 'delete', 'Delete users'),
    ('roles', 'create', 'Create roles'),
    ('roles', 'read', 'Read roles'),
    ('roles', 'update', 'Update roles'),
    ('roles', 'delete', 'Delete roles'),
    ('bookings', 'create', 'Create bookings'),
    ('bookings', 'read', 'Read bookings'),
    ('bookings', 'update', 'Update bookings'),
    ('bookings', 'delete', 'Delete bookings'),
    ('alerts', 'create', 'Create alerts'),
    ('alerts', 'read', 'Read alerts'),
    ('alerts', 'update', 'Update alerts'),
    ('alerts', 'delete', 'Delete alerts'),
    ('notifications', 'create', 'Create notifications'),
    ('notifications', 'read', 'Read notifications'),
    ('notifications', 'update', 'Update notifications'),
    ('notifications', 'delete', 'Delete notifications'),
    ('conversations', 'create', 'Create conversations'),
    ('conversations', 'read', 'Read conversations'),
    ('conversations', 'delete', 'Delete conversations')
ON CONFLICT (resource, action) DO NOTHING;
`;

// Function to assign permissions to roles
async function assignPermissionsToRoles(client) {
  // Admin permissions (all permissions)
  await client.query(`
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r, permissions p
    WHERE r.name = 'admin'
    ON CONFLICT DO NOTHING;
  `);

  // Manager permissions
  await client.query(`
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r, permissions p
    WHERE r.name = 'manager'
    AND (
      (p.resource = 'users' AND p.action IN ('read', 'update')) OR
      (p.resource = 'bookings') OR
      (p.resource = 'alerts') OR
      (p.resource = 'notifications') OR
      (p.resource = 'conversations' AND p.action IN ('read'))
    )
    ON CONFLICT DO NOTHING;
  `);

  // Staff permissions
  await client.query(`
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r, permissions p
    WHERE r.name = 'staff'
    AND (
      (p.resource = 'bookings' AND p.action IN ('read', 'update')) OR
      (p.resource = 'alerts' AND p.action IN ('read', 'update')) OR
      (p.resource = 'notifications' AND p.action IN ('create', 'read'))
    )
    ON CONFLICT DO NOTHING;
  `);

  // Guest permissions
  await client.query(`
    INSERT INTO role_permissions (role_id, permission_id)
    SELECT r.id, p.id
    FROM roles r, permissions p
    WHERE r.name = 'guest'
    AND (
      (p.resource = 'bookings' AND p.action = 'read') OR
      (p.resource = 'alerts' AND p.action IN ('create', 'read')) OR
      (p.resource = 'notifications' AND p.action = 'read') OR
      (p.resource = 'conversations' AND p.action = 'create')
    )
    ON CONFLICT DO NOTHING;
  `);
}

// Main function to initialize the database
async function initializeDatabase() {
  const client = await pool.connect();
  
  try {
    console.log('Starting database initialization...');
    
    // Begin transaction
    await client.query('BEGIN');
    
    // Create authentication tables
    console.log('Creating authentication tables...');
    await client.query(createAuthTables);
    
    // Create conversation tables
    console.log('Creating conversation history tables...');
    await client.query(createConversationTables);
    
    // Insert default roles
    console.log('Inserting default roles...');
    await client.query(insertDefaultRoles);
    
    // Insert default permissions
    console.log('Inserting default permissions...');
    await client.query(insertDefaultPermissions);
    
    // Assign permissions to roles
    console.log('Assigning permissions to roles...');
    await assignPermissionsToRoles(client);
    
    // Commit transaction
    await client.query('COMMIT');
    
    console.log('Database initialization completed successfully!');
  } catch (error) {
    // Rollback transaction on error
    await client.query('ROLLBACK');
    console.error('Error initializing database:', error);
  } finally {
    // Release client
    client.release();
    
    // Close pool
    await pool.end();
  }
}

// Run the initialization
initializeDatabase();