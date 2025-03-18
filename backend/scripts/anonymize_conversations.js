/**
 * Conversation Anonymization Script
 * 
 * This script anonymizes conversation data that is older than a specified number of days.
 * It removes personally identifiable information (PII) from conversation messages.
 * 
 * Usage: node anonymize_conversations.js
 * 
 * Environment variables:
 * - ANONYMIZE_AFTER_DAYS: Number of days after which conversations should be anonymized (default: 30)
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
const ANONYMIZE_AFTER_DAYS = parseInt(process.env.ANONYMIZE_AFTER_DAYS || '30', 10);

// PII patterns for detection and anonymization
const PII_PATTERNS = [
  // Email addresses
  { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, replacement: '[EMAIL REDACTED]' },
  
  // Phone numbers (various formats)
  { pattern: /\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g, replacement: '[PHONE REDACTED]' },
  
  // Credit card numbers
  { pattern: /\b(?:\d{4}[- ]?){3}\d{4}\b/g, replacement: '[CREDIT CARD REDACTED]' },
  
  // Social Security Numbers
  { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[SSN REDACTED]' },
  
  // Addresses
  { pattern: /\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Lane|Ln|Way|Parkway|Pkwy)\b/gi, replacement: '[ADDRESS REDACTED]' },
  
  // Names (more complex, would need NER for better accuracy)
  { pattern: /\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\b/g, replacement: '[NAME REDACTED]' },
  
  // Dates of birth
  { pattern: /\b(?:0?[1-9]|1[0-2])[\/.-](?:0?[1-9]|[12][0-9]|3[01])[\/.-](?:19|20)\d{2}\b/g, replacement: '[DOB REDACTED]' },
  
  // IP addresses
  { pattern: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g, replacement: '[IP REDACTED]' },
  
  // Room numbers (specific to hotel context)
  { pattern: /\broom\s+(\d{1,4}[A-Z]?)\b/gi, replacement: 'room [ROOM NUMBER]' },
  { pattern: /\b(?:my|your|the)\s+room\s+(?:number\s+)?(?:is\s+)?(\d{1,4}[A-Z]?)\b/gi, replacement: '$1 room [ROOM NUMBER]' }
];

/**
 * Anonymize text by replacing PII with placeholders
 * @param {string} text - Text to anonymize
 * @returns {string} - Anonymized text
 */
function anonymizeText(text) {
  if (!text) return text;
  
  let anonymizedText = text;
  
  // Apply each PII pattern
  for (const { pattern, replacement } of PII_PATTERNS) {
    anonymizedText = anonymizedText.replace(pattern, replacement);
  }
  
  return anonymizedText;
}

/**
 * Get conversation sessions to anonymize
 * @returns {Promise<Array>} - Array of conversation sessions
 */
async function getSessionsToAnonymize() {
  const client = await pool.connect();
  try {
    const result = await client.query(
      `SELECT id, user_id
       FROM conversation_sessions
       WHERE created_at < NOW() - INTERVAL '${ANONYMIZE_AFTER_DAYS} days'
       AND anonymized = false
       LIMIT 100`
    );
    
    return result.rows;
  } finally {
    client.release();
  }
}

/**
 * Anonymize messages in a conversation session
 * @param {number} sessionId - Conversation session ID
 * @returns {Promise<number>} - Number of messages anonymized
 */
async function anonymizeSessionMessages(sessionId) {
  const client = await pool.connect();
  try {
    // Get messages for the session
    const messagesResult = await client.query(
      `SELECT id, content, metadata
       FROM conversation_messages
       WHERE session_id = $1
       AND role = 'user'`, // Only anonymize user messages
      [sessionId]
    );
    
    let anonymizedCount = 0;
    
    // Anonymize each message
    for (const message of messagesResult.rows) {
      const anonymizedContent = anonymizeText(message.content);
      
      // Anonymize metadata
      let metadata = message.metadata || {};
      if (typeof metadata === 'string') {
        try {
          metadata = JSON.parse(metadata);
        } catch (e) {
          metadata = {};
        }
      }
      
      // Remove sensitive metadata
      delete metadata.ip;
      delete metadata.userAgent;
      
      // Update the message
      await client.query(
        `UPDATE conversation_messages
         SET content = $1, metadata = $2
         WHERE id = $3`,
        [anonymizedContent, JSON.stringify(metadata), message.id]
      );
      
      anonymizedCount++;
    }
    
    // Mark the session as anonymized
    await client.query(
      `UPDATE conversation_sessions
       SET anonymized = true
       WHERE id = $1`,
      [sessionId]
    );
    
    return anonymizedCount;
  } finally {
    client.release();
  }
}

/**
 * Remove user association from conversation sessions
 * @param {number} userId - User ID
 * @returns {Promise<number>} - Number of sessions updated
 */
async function removeUserAssociation(userId) {
  const client = await pool.connect();
  try {
    const result = await client.query(
      `UPDATE conversation_sessions
       SET user_id = NULL
       WHERE user_id = $1
       AND created_at < NOW() - INTERVAL '${ANONYMIZE_AFTER_DAYS} days'
       AND anonymized = true`,
      [userId]
    );
    
    return result.rowCount;
  } finally {
    client.release();
  }
}

/**
 * Main function to anonymize conversations
 */
async function anonymizeConversations() {
  try {
    console.log('Starting conversation anonymization process...');
    console.log(`Anonymizing conversations older than ${ANONYMIZE_AFTER_DAYS} days`);
    
    // Get sessions to anonymize
    const sessions = await getSessionsToAnonymize();
    console.log(`Found ${sessions.length} conversation sessions to anonymize`);
    
    if (sessions.length === 0) {
      console.log('No conversations to anonymize');
      return;
    }
    
    // Track users for association removal
    const userIds = new Set();
    
    // Anonymize each session
    let totalMessagesAnonymized = 0;
    for (const session of sessions) {
      const messagesAnonymized = await anonymizeSessionMessages(session.id);
      totalMessagesAnonymized += messagesAnonymized;
      
      console.log(`Anonymized ${messagesAnonymized} messages in session ${session.id}`);
      
      // Add user ID to set for later processing
      if (session.user_id) {
        userIds.add(session.user_id);
      }
    }
    
    console.log(`Total messages anonymized: ${totalMessagesAnonymized}`);
    
    // Remove user associations
    for (const userId of userIds) {
      const sessionsUpdated = await removeUserAssociation(userId);
      console.log(`Removed user association from ${sessionsUpdated} sessions for user ${userId}`);
    }
    
    console.log('Conversation anonymization completed successfully');
  } catch (error) {
    console.error('Error anonymizing conversations:', error);
  } finally {
    // Close pool
    await pool.end();
  }
}

// Run the anonymization process
anonymizeConversations();