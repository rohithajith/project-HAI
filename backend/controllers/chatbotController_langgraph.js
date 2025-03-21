const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

// Configuration for the LangGraph AI Assistant API
const AI_ASSISTANT_API_URL = process.env.AI_ASSISTANT_API_URL || 'http://localhost:8000';
const AI_ASSISTANT_API_TIMEOUT = parseInt(process.env.AI_ASSISTANT_API_TIMEOUT || '30000', 10);

// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'you are a helpful hotel AI assistant which acts like hotel reception updating requests and handling queries from users';

/**
 * Process a chat message using the LangGraph multi-agent system
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const processMessage = async (req, res) => {
  try {
    const { message, history = [], conversation_id = null } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Prepare history with system prompt if not already present
    let chatHistory = [...history];
    if (!chatHistory.some(msg => msg.role === 'system')) {
      chatHistory.unshift({
        role: 'system',
        content: SYSTEM_PROMPT
      });
    }

    // Add the new user message
    chatHistory.push({
      role: 'user',
      content: message
    });

    console.log(`Processing message for conversation: ${conversation_id || 'new conversation'}`);

    // Call the LangGraph AI Assistant API
    const response = await axios.post(
      `${AI_ASSISTANT_API_URL}/api/chat`,
      {
        messages: chatHistory,
        conversation_id
      },
      {
        timeout: AI_ASSISTANT_API_TIMEOUT,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );

    // Extract the assistant's response
    const result = response.data;
    
    // Get the last assistant message
    const assistantMessages = result.messages.filter(msg => msg.role === 'assistant');
    const lastAssistantMessage = assistantMessages.length > 0 
      ? assistantMessages[assistantMessages.length - 1].content 
      : 'I apologize, but I couldn\'t process your request at the moment.';

    // Check if there are any actions that need to be processed
    if (result.agent_outputs && Object.keys(result.agent_outputs).length > 0) {
      // Process agent actions (e.g., update database, send notifications)
      processAgentActions(result.agent_outputs);
    }

    return res.json({
      response: lastAssistantMessage,
      conversation_id: result.conversation_id,
      messages: result.messages
    });
  } catch (error) {
    console.error('Error processing chatbot message:', error);
    
    // Handle specific error types
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error Response:', error.response.data);
      return res.status(error.response.status).json({ 
        error: error.response.data.detail || 'Error from AI Assistant API' 
      });
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from AI Assistant API');
      return res.status(503).json({ 
        error: 'AI Assistant service unavailable. Please try again later.' 
      });
    }
    
    return res.status(500).json({ error: 'Internal server error' });
  }
};

/**
 * Process actions from the AI agents
 * @param {Object} agentOutputs - Outputs from the agents
 */
const processAgentActions = (agentOutputs) => {
  // Log the agent outputs
  console.log('Processing agent actions:', JSON.stringify(agentOutputs, null, 2));
  
  // Process each agent's actions
  Object.entries(agentOutputs).forEach(([agentName, output]) => {
    if (output.actions && output.actions.length > 0) {
      output.actions.forEach(action => {
        // Handle different action types
        switch (action.type) {
          case 'update_booking':
            console.log(`Updating booking ${action.booking_id} to status: ${action.status}`);
            // In a real implementation, this would update the database
            break;
            
          case 'create_service_request':
            console.log(`Creating service request for room ${action.room_number}: ${action.request_type}`);
            // In a real implementation, this would create a service request
            break;
            
          case 'send_notification':
            console.log(`Sending notification to ${action.recipient}: ${action.message}`);
            // In a real implementation, this would send a notification
            break;
            
          case 'log_wellness_session':
            console.log(`Logging wellness session: ${action.session_type}`);
            // In a real implementation, this would log the wellness session
            break;
            
          default:
            console.log(`Unknown action type: ${action.type}`);
        }
      });
    }
  });
};

/**
 * Get conversation history
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const getConversation = async (req, res) => {
  try {
    const { conversation_id } = req.params;
    
    if (!conversation_id) {
      return res.status(400).json({ error: 'Conversation ID is required' });
    }
    
    // Call the LangGraph AI Assistant API
    const response = await axios.get(
      `${AI_ASSISTANT_API_URL}/api/conversations/${conversation_id}`,
      {
        timeout: AI_ASSISTANT_API_TIMEOUT
      }
    );
    
    return res.json(response.data);
  } catch (error) {
    console.error('Error getting conversation:', error);
    return res.status(500).json({ error: 'Error getting conversation' });
  }
};

/**
 * Delete a conversation
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const deleteConversation = async (req, res) => {
  try {
    const { conversation_id } = req.params;
    
    if (!conversation_id) {
      return res.status(400).json({ error: 'Conversation ID is required' });
    }
    
    // Call the LangGraph AI Assistant API
    await axios.delete(
      `${AI_ASSISTANT_API_URL}/api/conversations/${conversation_id}`,
      {
        timeout: AI_ASSISTANT_API_TIMEOUT
      }
    );
    
    return res.json({ success: true });
  } catch (error) {
    console.error('Error deleting conversation:', error);
    return res.status(500).json({ error: 'Error deleting conversation' });
  }
};

/**
 * Check the health of the AI Assistant API
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const healthCheck = async (req, res) => {
  try {
    // Call the LangGraph AI Assistant API health check endpoint
    const response = await axios.get(
      `${AI_ASSISTANT_API_URL}/api/health`,
      {
        timeout: 5000 // Short timeout for health check
      }
    );
    
    return res.json({ status: 'healthy', api_status: response.data.status });
  } catch (error) {
    console.error('AI Assistant API health check failed:', error);
    return res.status(503).json({ status: 'unhealthy', error: 'AI Assistant API is not available' });
  }
};

module.exports = {
  processMessage,
  getConversation,
  deleteConversation,
  healthCheck
};