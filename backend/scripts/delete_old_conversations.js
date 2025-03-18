/**
 * Delete Old Conversations Script
 * 
 * This script deletes conversation data that is older than the specified retention period.
 * It helps maintain compliance with data retention policies and reduces database size.
 * 
 * Usage: node delete_old_conversations.js
 * 
 * Environment variables:
 * - DATA_RETENTION_DAYS: Number of days to retain conversation data (default: 90)
 */

const { Pool } = require('pg');
const dotenv = require('dotenv');
const path = require('path');

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

// Configuration
const DATA_RETENTION_DAYS = parseInt(process.env.DATA_RETENTION_DAYS || '90', 10);

/**
 * Get conversation sessions to delete
 * @returns {Promise<Array>} - Array of conversation session IDs
 */
async function getSessionsToDelete() {
  const client = await pool.connect();
  try {
    const result = await client.query(
      `SELECT id
       FROM conversation_sessions
       WHERE created_at < NOW() - INTERVAL '${DATA_RETENTION_DAYS} days'
       LIMIT 100`
    );
    
    return result.rows.map(row => row.id);
  } finally {
    client.release();
  }
}

/**
 * Delete conversation sessions and related data
 * @param {Array<number>} sessionIds - Array of session IDs to delete
 * @returns {Promise<number>} - Number of sessions deleted
 */
async function deleteConversationSessions(sessionIds) {
  if (sessionIds.length === 0) {
    return 0;
  }
  
  const client = await pool.connect();
  try {
    // Start transaction
    await client.query('BEGIN');
    
    // Delete conversation messages (cascade will handle LLM metrics)
    const messagesResult = await client.query(
      `DELETE FROM conversation_messages
       WHERE session_id = ANY($1)
       RETURNING id`,
      [sessionIds]
    );
    
    const deletedMessageCount = messagesResult.rowCount;
    
    // Delete conversation sessions
    const sessionsResult = await client.query(
      `DELETE FROM conversation_sessions
       WHERE id = ANY($1)`,
      [sessionIds]
    );
    
    const deletedSessionCount = sessionsResult.rowCount;
    
    // Commit transaction
    await client.query('COMMIT');
    
    return {
      sessions: deletedSessionCount,
      messages: deletedMessageCount
    };
  } catch (error) {
    // Rollback transaction on error
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}

/**
 * Main function to delete old conversations
 */
async function deleteOldConversations() {
  try {
    console.log('Starting deletion of old conversations...');
    console.log(`Deleting conversations older than ${DATA_RETENTION_DAYS} days`);
    
    // Process in batches to avoid memory issues with large datasets
    let totalSessionsDeleted = 0;
    let totalMessagesDeleted = 0;
    let batchCount = 0;
    
    while (true) {
      // Get sessions to delete
      const sessionIds = await getSessionsToDelete();
      
      if (sessionIds.length === 0) {
        console.log('No more conversations to delete');
        break;
      }
      
      // Delete sessions and related data
      const { sessions, messages } = await deleteConversationSessions(sessionIds);
      
      totalSessionsDeleted += sessions;
      totalMessagesDeleted += messages;
      batchCount++;
      
      console.log(`Batch ${batchCount}: Deleted ${sessions} sessions and ${messages} messages`);
      
      // Break if we deleted fewer sessions than the limit
      if (sessions < 100) {
        break;
      }
    }
    
    console.log(`Total sessions deleted: ${totalSessionsDeleted}`);
    console.log(`Total messages deleted: ${totalMessagesDeleted}`);
    console.log('Deletion of old conversations completed successfully');
  } catch (error) {
    console.error('Error deleting old conversations:', error);
  } finally {
    // Close pool
    await pool.end();
  }
}

// Run the deletion process
deleteOldConversations();