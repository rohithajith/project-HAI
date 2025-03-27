const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { getIO } = require('../services/socketService'); // Import socket service

// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users';

// Note: Using a locally downloaded GPT-2 model
const USE_LOCAL_MODEL = true; // Set to false to use the Hugging Face API instead

/**
 * Process a chat message using the Python backend (agents + LLM fallback)
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const processMessage = async (req, res) => {
  try {
    const { message, history = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Prepare history (system prompt logic seems fine, keep it)
    let chatHistory = [...history];
    // Note: The Python script now also handles the system prompt logic if needed,
    // but sending it pre-formatted might still be useful for context.
    if (!chatHistory.some(msg => msg.role === 'system')) {
       chatHistory.unshift({
         role: 'system',
         content: SYSTEM_PROMPT
       });
    }

    // Convert history to JSON string for the Python script
    // Ensure proper escaping for command line execution
    const historyJson = JSON.stringify(chatHistory).replace(/"/g, '\\"');
    const escapedMessage = message.replace(/"/g, '\\"');

    // Path to the Python script
    const scriptPath = path.join(__dirname, '..', USE_LOCAL_MODEL ? 'local_model_chatbot.py' : 'chatbot_bridge.py'); // Assuming local_model_chatbot.py is the target

    // Check if the script exists
    if (!fs.existsSync(scriptPath)) {
      console.error(`Script not found: ${scriptPath}`);
      return res.status(500).json({
        error: `Backend script not found: ${path.basename(scriptPath)}`
      });
    }

    console.log(`Executing Python script: ${path.basename(scriptPath)}`);

    // Execute the Python script
    // Increased maxBuffer size in case of large JSON output
    exec(
      `python "${scriptPath}" --message "${escapedMessage}" --history "${historyJson}"`,
      { maxBuffer: 1024 * 1024 * 5 }, // 5MB buffer
      (error, stdout, stderr) => {
        if (error) {
          console.error(`Error executing Python script: ${error.message}`);
          console.error(`Stderr: ${stderr}`); // Log stderr on error
          return res.status(500).json({ error: 'Error processing message via backend script' });
        }

        if (stderr) {
          // Log stderr even if no error code, might contain warnings/logs from Python
          console.warn(`Python script stderr: ${stderr}`);
        }

        try {
          // DETAILED LOG: Log raw output from Python script
          console.log('DEBUG: Raw stdout from Python:', stdout);

          // Attempt to parse the full JSON response from the Python script
          const result = JSON.parse(stdout);

          // DETAILED LOG: Log the parsed result object
          console.log('DEBUG: Parsed result from Python:', JSON.stringify(result, null, 2));

          // Check for errors reported by the Python script itself
          if (result.error) {
            console.error(`Python script reported error: ${result.error}`);
            // Send Python's error message back if available, otherwise generic
            return res.status(500).json({ error: result.error || 'Backend script encountered an error' });
          }

          // --- Handle Notifications ---
          // DETAILED LOG: Check if notifications array exists and has items
          console.log(`DEBUG: Checking for notifications. Found: ${result.notifications ? result.notifications.length : 'None'}`);
          if (result.notifications && Array.isArray(result.notifications) && result.notifications.length > 0) {
            try {
              const io = getIO(); // Get Socket.IO instance
              result.notifications.forEach(notification => {
                if (notification.event && notification.payload) {
                  console.log(`Emitting WebSocket event: ${notification.event}`, notification.payload);
                  io.emit(notification.event, notification.payload); // Broadcast the event
                } else {
                  console.warn('Received invalid notification format from Python:', notification);
                }
              });
            } catch (socketError) {
              console.error('Error getting Socket.IO instance or emitting event:', socketError);
              // Continue processing, but log the error
            }
          }
          // --- End Handle Notifications ---

          // Send only the text response back to the chatbot UI via HTTP
          return res.json({ response: result.response || "Processing complete." }); // Ensure response is not undefined

        } catch (parseError) {
          console.error('Error parsing Python script output:', parseError);
          console.error('Raw stdout:', stdout); // Log raw output for debugging
          return res.status(500).json({ error: 'Error parsing response from backend script' });
        }
      }
    );
  } catch (error) {
    console.error('Critical error in processMessage controller:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = {
  processMessage
};