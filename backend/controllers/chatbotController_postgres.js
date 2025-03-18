const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const db = require('../config/database_postgres');

// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users';

// Note: Using a locally downloaded GPT-2 model
const USE_LOCAL_MODEL = true; // Set to false to use the Hugging Face API instead

/**
 * Check if user has given consent for data collection
 * @param {number} userId - User ID
 * @returns {Promise<Object>} - User's consent preferences
 */
const getUserConsent = async (userId) => {
  if (!userId) return null;
  
  try {
    // Check if user has given consent
    const consent = await db.queryOne(
      'SELECT * FROM data_consent WHERE user_id = $1',
      [userId]
    );
    
    return consent;
  } catch (error) {
    console.error('Error checking user consent:', error);
    return null;
  }
};

/**
 * Create or get an existing conversation session
 * @param {number} userId - User ID (optional)
 * @param {boolean} consentObtained - Whether consent was obtained
 * @returns {Promise<Object>} - Conversation session
 */
const createOrGetSession = async (userId, consentObtained = false) => {
  try {
    // Generate a unique session ID
    const sessionId = uuidv4();
    
    // Create a new session
    const result = await db.insert(
      `INSERT INTO conversation_sessions 
       (user_id, session_id, consent_obtained) 
       VALUES ($1, $2, $3) 
       RETURNING id`,
      [userId || null, sessionId, consentObtained]
    );
    
    return {
      id: result,
      sessionId,
      userId,
      consentObtained
    };
  } catch (error) {
    console.error('Error creating conversation session:', error);
    throw error;
  }
};

/**
 * Store a message in the conversation history
 * @param {number} sessionId - Conversation session ID
 * @param {string} role - Message role ('user', 'assistant', 'system')
 * @param {string} content - Message content
 * @param {number} messageIndex - Message index in the conversation
 * @param {Object} metadata - Additional metadata
 * @returns {Promise<number>} - Message ID
 */
const storeMessage = async (sessionId, role, content, messageIndex, metadata = {}) => {
  try {
    const messageId = await db.insert(
      `INSERT INTO conversation_messages 
       (session_id, message_index, role, content, metadata) 
       VALUES ($1, $2, $3, $4, $5) 
       RETURNING id`,
      [sessionId, messageIndex, role, content, JSON.stringify(metadata)]
    );
    
    return messageId;
  } catch (error) {
    console.error('Error storing message:', error);
    return null;
  }
};

/**
 * Store LLM metrics
 * @param {number} messageId - Message ID
 * @param {string} modelName - Model name
 * @param {number} tokensInput - Number of input tokens
 * @param {number} tokensOutput - Number of output tokens
 * @param {number} latencyMs - Latency in milliseconds
 * @param {Object} metadata - Additional metadata
 * @returns {Promise<number>} - Metrics ID
 */
const storeLLMMetrics = async (messageId, modelName, tokensInput, tokensOutput, latencyMs, metadata = {}) => {
  try {
    const metricsId = await db.insert(
      `INSERT INTO llm_metrics 
       (message_id, model_name, tokens_input, tokens_output, latency_ms, metadata) 
       VALUES ($1, $2, $3, $4, $5, $6) 
       RETURNING id`,
      [messageId, modelName, tokensInput, tokensOutput, latencyMs, JSON.stringify(metadata)]
    );
    
    return metricsId;
  } catch (error) {
    console.error('Error storing LLM metrics:', error);
    return null;
  }
};

/**
 * End a conversation session
 * @param {number} sessionId - Conversation session ID
 * @returns {Promise<boolean>} - Success status
 */
const endConversationSession = async (sessionId) => {
  try {
    await db.execute(
      'UPDATE conversation_sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = $1',
      [sessionId]
    );
    
    return true;
  } catch (error) {
    console.error('Error ending conversation session:', error);
    return false;
  }
};

/**
 * Process a chat message using either the local model or the Hugging Face API
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const processMessage = async (req, res) => {
  let sessionId = null;
  let startTime = Date.now();
  
  try {
    const { message, history = [], sessionToken } = req.body;
    const userId = req.user?.id; // Get user ID if authenticated

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Check user consent if authenticated
    let consentObtained = false;
    if (userId) {
      const consent = await getUserConsent(userId);
      consentObtained = consent?.service_improvement || false;
    }

    // Create or get conversation session
    let session;
    if (sessionToken) {
      // Get existing session
      const existingSession = await db.queryOne(
        'SELECT id, user_id, consent_obtained FROM conversation_sessions WHERE session_id = $1',
        [sessionToken]
      );
      
      if (existingSession) {
        session = {
          id: existingSession.id,
          sessionId: sessionToken,
          userId: existingSession.user_id,
          consentObtained: existingSession.consent_obtained
        };
      } else {
        // Create new session if token is invalid
        session = await createOrGetSession(userId, consentObtained);
      }
    } else {
      // Create new session
      session = await createOrGetSession(userId, consentObtained);
    }
    
    sessionId = session.id;

    // Prepare history with system prompt if not already present
    let chatHistory = [...history];
    if (!chatHistory.some(msg => msg.content.includes(SYSTEM_PROMPT))) {
      chatHistory.unshift({
        role: 'system',
        content: SYSTEM_PROMPT
      });
    }

    // Store user message if consent obtained
    let userMessageId = null;
    if (session.consentObtained) {
      userMessageId = await storeMessage(
        session.id,
        'user',
        message,
        chatHistory.length,
        { ip: req.ip, userAgent: req.headers['user-agent'] }
      );
    }

    // Convert history to JSON string for the Python script
    const historyJson = JSON.stringify(chatHistory);
    
    // Path to the Python script (local model or API bridge)
    const scriptPath = path.join(__dirname, '..', USE_LOCAL_MODEL ? 'local_model_chatbot.py' : 'chatbot_bridge.py');
    
    // Check if the script exists
    if (!fs.existsSync(scriptPath)) {
      console.error(`Script not found: ${scriptPath}`);
      return res.status(500).json({
        error: `Script not found: ${USE_LOCAL_MODEL ? 'local_model_chatbot.py' : 'chatbot_bridge.py'}`
      });
    }
    
    console.log(`Using ${USE_LOCAL_MODEL ? 'local model' : 'Hugging Face API'} for chatbot response`);
    
    // Execute the Python script
    exec(
      `python "${scriptPath}" --message "${message.replace(/"/g, '\\"')}" --history "${historyJson.replace(/"/g, '\\"')}"`,
      async (error, stdout, stderr) => {
        const endTime = Date.now();
        const latencyMs = endTime - startTime;
        
        if (error) {
          console.error(`Error executing Python script: ${error.message}`);
          return res.status(500).json({ error: 'Error processing message' });
        }
        
        if (stderr) {
          console.error(`Python script stderr: ${stderr}`);
        }
        
        try {
          // Parse the JSON response from the Python script
          const result = JSON.parse(stdout);
          
          if (result.error) {
            return res.status(500).json({ error: result.error });
          }
          
          // Store assistant message if consent obtained
          if (session.consentObtained) {
            const assistantMessageId = await storeMessage(
              session.id,
              'assistant',
              result.response,
              chatHistory.length + 1,
              {}
            );
            
            // Store LLM metrics if available
            if (assistantMessageId) {
              // Extract metrics from result or use defaults
              const metrics = result.metrics || {};
              await storeLLMMetrics(
                assistantMessageId,
                metrics.model_name || 'gpt2',
                metrics.tokens_input || message.length / 4, // Rough estimate
                metrics.tokens_output || result.response.length / 4, // Rough estimate
                latencyMs,
                { model: USE_LOCAL_MODEL ? 'local' : 'api' }
              );
            }
          }
          
          return res.json({ 
            response: result.response,
            sessionToken: session.sessionId
          });
        } catch (parseError) {
          console.error('Error parsing Python script output:', parseError);
          console.error('Raw output:', stdout);
          return res.status(500).json({ error: 'Error parsing response' });
        }
      }
    );
  } catch (error) {
    console.error('Error processing chatbot message:', error);
    
    // End session if there was an error
    if (sessionId) {
      await endConversationSession(sessionId);
    }
    
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Update user consent preferences
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const updateConsent = async (req, res) => {
  try {
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    const { serviceImprovement, modelTraining, analytics, marketing } = req.body;
    
    // Check if consent record exists
    const existingConsent = await db.queryOne(
      'SELECT id FROM data_consent WHERE user_id = $1',
      [userId]
    );
    
    if (existingConsent) {
      // Update existing consent
      await db.execute(
        `UPDATE data_consent 
         SET service_improvement = $1, model_training = $2, analytics = $3, marketing = $4,
             last_updated_at = CURRENT_TIMESTAMP
         WHERE user_id = $5`,
        [
          serviceImprovement || false,
          modelTraining || false,
          analytics || false,
          marketing || false,
          userId
        ]
      );
    } else {
      // Create new consent record
      await db.execute(
        `INSERT INTO data_consent 
         (user_id, service_improvement, model_training, analytics, marketing, consent_given_at)
         VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)`,
        [
          userId,
          serviceImprovement || false,
          modelTraining || false,
          analytics || false,
          marketing || false
        ]
      );
    }
    
    return res.json({ 
      success: true,
      message: 'Consent preferences updated successfully'
    });
  } catch (error) {
    console.error('Error updating consent preferences:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Get user conversation history
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const getConversationHistory = async (req, res) => {
  try {
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    // Get conversation sessions
    const sessions = await db.query(
      `SELECT id, session_id, started_at, ended_at
       FROM conversation_sessions
       WHERE user_id = $1
       ORDER BY started_at DESC
       LIMIT 10`,
      [userId]
    );
    
    // Get messages for each session
    const sessionsWithMessages = await Promise.all(
      sessions.map(async (session) => {
        const messages = await db.query(
          `SELECT message_index, role, content, timestamp
           FROM conversation_messages
           WHERE session_id = $1
           ORDER BY message_index ASC`,
          [session.id]
        );
        
        return {
          ...session,
          messages
        };
      })
    );
    
    return res.json({ 
      success: true,
      conversations: sessionsWithMessages
    });
  } catch (error) {
    console.error('Error getting conversation history:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Delete user conversation history
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const deleteConversationHistory = async (req, res) => {
  try {
    const userId = req.user?.id;
    const { sessionId } = req.params;
    
    if (!userId) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    // Check if session belongs to user
    if (sessionId) {
      const session = await db.queryOne(
        'SELECT id FROM conversation_sessions WHERE session_id = $1 AND user_id = $2',
        [sessionId, userId]
      );
      
      if (!session) {
        return res.status(404).json({ error: 'Conversation session not found' });
      }
      
      // Delete specific session
      await db.execute(
        'DELETE FROM conversation_sessions WHERE id = $1',
        [session.id]
      );
      
      return res.json({ 
        success: true,
        message: 'Conversation session deleted successfully'
      });
    } else {
      // Delete all user sessions
      await db.execute(
        'DELETE FROM conversation_sessions WHERE user_id = $1',
        [userId]
      );
      
      return res.json({ 
        success: true,
        message: 'All conversation history deleted successfully'
      });
    }
  } catch (error) {
    console.error('Error deleting conversation history:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = {
  processMessage,
  updateConsent,
  getConversationHistory,
  deleteConversationHistory
};