const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const NotificationService = require('../services/notificationService');

// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'You are a helpful hotel AI which acts like hotel reception managing requests';

/**
 * Process a chat message using AI agents
 */
const processMessage = async (req, res) => {
  try {
    const { message, history = [], roomNumber, guestId } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Prepare history with system prompt
    let chatHistory = [...history];
    if (!chatHistory.some(msg => msg.content.includes(SYSTEM_PROMPT))) {
      chatHistory.unshift({
        role: 'system',
        content: SYSTEM_PROMPT
      });
    }

    // Process with appropriate AI agent
    let agentResult;
    if (message.toLowerCase().includes('laundry') ||
        message.toLowerCase().includes('towels') ||
        message.toLowerCase().includes('tea')) {
      // Handle service requests
      await NotificationService.sendRoomNotification(
        roomNumber,
        `Guest request: ${message}`
      );
      
      agentResult = { 
        response: `Thank you for your request! We're processing your ${message.includes('laundry') ? 
                  'laundry' : message.includes('towels') ? 
                  'towel' : 'tea'} service.`
      };
    } else {
      // Use AI agent for general queries
      const scriptPath = path.join(__dirname, '../ai_agents/run.py');
      const inputData = {
        messages: chatHistory,
        latest_message: message,
        guest_id: guestId,
        room_number: roomNumber
      };

      agentResult = await new Promise((resolve, reject) => {
        exec(
          `python "${scriptPath}" --agent hotel_info --input '${JSON.stringify(inputData)}'`,
          (error, stdout, stderr) => {
            if (error) {
              console.error(`Error executing AI agent: ${error.message}`);
              reject(error);
            }
            try {
              resolve(JSON.parse(stdout));
            } catch (e) {
              reject(e);
            }
          }
        );
      });
    }

    return res.json({ 
      response: agentResult.response,
      sessionToken: req.body.sessionToken
    });

  } catch (error) {
    console.error('Error processing chatbot message:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = {
  processMessage
};