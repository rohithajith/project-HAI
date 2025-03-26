const { spawn } = require('child_process'); // Use spawn instead of exec
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
    // Provide default null for guestId if not sent
    const { message, history = [], roomNumber, guestId = null } = req.body;

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

      // Use spawn to execute Python script and pipe data via stdin
      agentResult = await new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptPath, '--agent', 'hotel_info']);
        let stdoutData = '';
        let stderrData = '';

        // Write JSON data to stdin
        pythonProcess.stdin.write(JSON.stringify(inputData));
        pythonProcess.stdin.end();

        // Collect stdout
        pythonProcess.stdout.on('data', (data) => {
          stdoutData += data.toString();
        });

        // Collect stderr
        pythonProcess.stderr.on('data', (data) => {
          stderrData += data.toString();
        });

        // Handle process exit
        pythonProcess.on('close', (code) => {
          if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            console.error(`Stderr: ${stderrData}`);
            reject(new Error(`Python script failed with code ${code}: ${stderrData}`));
          } else {
            try {
              // Parse the JSON output from stdout
              resolve(JSON.parse(stdoutData));
            } catch (e) {
              console.error(`Error parsing Python script output: ${e}`);
              console.error(`Stdout: ${stdoutData}`);
              reject(new Error(`Failed to parse JSON output from Python script: ${e}`));
            }
          }
        });

        // Handle spawn errors
        pythonProcess.on('error', (error) => {
          console.error(`Failed to start Python script: ${error.message}`);
          reject(error);
        });
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