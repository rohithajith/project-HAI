const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// System prompt for the hotel AI assistant
const SYSTEM_PROMPT = 'you are a helpfull hotel ai which acts like hotel reception udating requests and handiling queries from users';

// Note: Using a locally downloaded GPT-2 model
const USE_LOCAL_MODEL = true; // Set to false to use the Hugging Face API instead

/**
 * Process a chat message using either the local model or the Hugging Face API
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
const processMessage = async (req, res) => {
  try {
    const { message, history = [] } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Prepare history with system prompt if not already present
    let chatHistory = [...history];
    if (!chatHistory.some(msg => msg.content.includes(SYSTEM_PROMPT))) {
      chatHistory.unshift({
        role: 'system',
        content: SYSTEM_PROMPT
      });
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
      (error, stdout, stderr) => {
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
          
          return res.json({ response: result.response });
        } catch (parseError) {
          console.error('Error parsing Python script output:', parseError);
          console.error('Raw output:', stdout);
          return res.status(500).json({ error: 'Error parsing response' });
        }
      }
    );
  } catch (error) {
    console.error('Error processing chatbot message:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

module.exports = {
  processMessage
};