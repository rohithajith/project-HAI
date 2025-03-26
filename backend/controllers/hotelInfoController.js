/**
 * Hotel Information Controller
 * 
 * This controller handles requests for hotel information using the Python-based
 * RAG-enabled hotel information agent.
 */

const { spawn } = require('child_process');
const path = require('path');
const logger = require('../services/loggerService');

/**
 * Get hotel information based on user query
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getHotelInfo = async (req, res) => {
  try {
    const { message, history, guestName, bookingId, queryType } = req.body;

    if (!message) {
      return res.status(400).json({
        status: 'error',
        message: 'Message is required'
      });
    }

    logger.info(`Hotel info request: ${message.substring(0, 50)}...`);

    // Prepare input for the Python agent
    const input = {
      guest_name: guestName || null,
      booking_id: bookingId || null,
      messages: history || [],
      query_type: queryType || null,
      latest_message: message
    };

    // Convert to JSON string
    const inputJson = JSON.stringify(input);

    // Call the Python agent
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ai_agents/run.py'),
      '--agent', 'hotel_info',
      '--input', inputJson
    ]);

    let outputData = '';
    let errorData = '';

    // Collect data from the Python process
    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      logger.error(`Hotel info agent error: ${data.toString()}`);
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        logger.error(`Hotel info agent process exited with code ${code}`);
        logger.error(`Error: ${errorData}`);
        
        return res.status(500).json({
          status: 'error',
          message: 'Error processing hotel information request',
          error: errorData
        });
      }

      try {
        // Parse the output JSON
        const output = JSON.parse(outputData);
        
        // Return the response
        return res.status(200).json({
          status: 'success',
          data: output
        });
      } catch (error) {
        logger.error(`Error parsing hotel info agent output: ${error.message}`);
        
        return res.status(500).json({
          status: 'error',
          message: 'Error parsing hotel information response',
          error: error.message
        });
      }
    });
  } catch (error) {
    logger.error(`Hotel info controller error: ${error.message}`);
    
    return res.status(500).json({
      status: 'error',
      message: 'Error processing hotel information request',
      error: error.message
    });
  }
};

/**
 * Initialize the RAG module with hotel information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.initializeRag = async (req, res) => {
  try {
    const { clear } = req.query;
    
    // Call the Python script to initialize the RAG module
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ai_agents/rag/init_rag.py'),
      clear === 'true' ? '--clear' : ''
    ].filter(Boolean));

    let outputData = '';
    let errorData = '';

    // Collect data from the Python process
    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
      logger.info(`RAG initialization: ${data.toString()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      logger.error(`RAG initialization error: ${data.toString()}`);
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        logger.error(`RAG initialization process exited with code ${code}`);
        
        return res.status(500).json({
          status: 'error',
          message: 'Error initializing RAG module',
          error: errorData
        });
      }

      return res.status(200).json({
        status: 'success',
        message: 'RAG module initialized successfully',
        details: outputData
      });
    });
  } catch (error) {
    logger.error(`RAG initialization controller error: ${error.message}`);
    
    return res.status(500).json({
      status: 'error',
      message: 'Error initializing RAG module',
      error: error.message
    });
  }
};

/**
 * Get RAG status
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.handleTowelRequest = async (req, res) => {
    try {
        const { request } = req.body;
        
        if (!request) {
            return res.status(400).json({
                status: 'error',
                message: 'Request is required'
            });
        }

        logger.info(`Towel request received: ${request.substring(0, 50)}...`);

        // Here you would typically:
        // 1. Create a task in your task management system
        // 2. Send a notification to housekeeping
        // 3. Log the request in your database
        
        return res.status(200).json({
            status: 'success',
            message: 'Towel request processed successfully',
            request: request
        });
    } catch (error) {
        logger.error(`Towel request error: ${error.message}`);
        
        return res.status(500).json({
            status: 'error',
            message: 'Error processing towel request',
            error: error.message
        });
    }
};

/**
 * Get room data information
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.getRoomData = async (req, res) => {
  try {
    // Call the Python room service agent
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ai_agents/run.py'),
      '--agent', 'room_service',
      '--input', JSON.stringify(req.body)
    ]);

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      logger.error(`Room data error: ${data.toString()}`);
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        return res.status(500).json({
          status: 'error',
          message: 'Error getting room data',
          error: errorData
        });
      }

      try {
        const output = JSON.parse(outputData);
        return res.status(200).json({
          status: 'success',
          data: output
        });
      } catch (error) {
        return res.status(500).json({
          status: 'error',
          message: 'Error parsing room data response',
          error: error.message
        });
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      message: 'Error processing room data request',
      error: error.message
    });
  }
};

/**
 * Handle chat requests
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 */
exports.handleChat = async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({
        status: 'error',
        message: 'Message is required'
      });
    }

    // Call the Python hotel info agent
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ai_agents/run.py'),
      '--agent', 'hotel_info',
      '--input', JSON.stringify({ latest_message: message })
    ]);

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      logger.error(`Chat error: ${data.toString()}`);
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        return res.status(500).json({
          status: 'error',
          message: 'Error processing chat request',
          error: errorData
        });
      }

      try {
        const output = JSON.parse(outputData);
        return res.status(200).json({
          status: 'success',
          data: output
        });
      } catch (error) {
        return res.status(500).json({
          status: 'error',
          message: 'Error parsing chat response',
          error: error.message
        });
      }
    });
  } catch (error) {
    return res.status(500).json({
      status: 'error',
      message: 'Error processing chat request',
      error: error.message
    });
  }
};

exports.getRagStatus = async (req, res) => {
  try {
    // Call the Python script to check RAG status
    const pythonProcess = spawn('python', [
      path.join(__dirname, '../ai_agents/run.py'),
      '--agent', 'rag_status'
    ]);

    let outputData = '';
    let errorData = '';

    // Collect data from the Python process
    pythonProcess.stdout.on('data', (data) => {
      outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      logger.error(`RAG status error: ${data.toString()}`);
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        logger.error(`RAG status process exited with code ${code}`);
        
        return res.status(500).json({
          status: 'error',
          message: 'Error checking RAG status',
          error: errorData
        });
      }

      try {
        // Parse the output JSON
        const output = JSON.parse(outputData);
        
        // Return the response
        return res.status(200).json({
          status: 'success',
          data: output
        });
      } catch (error) {
        logger.error(`Error parsing RAG status output: ${error.message}`);
        
        return res.status(500).json({
          status: 'error',
          message: 'Error parsing RAG status response',
          error: error.message
        });
      }
    });
  } catch (error) {
    logger.error(`RAG status controller error: ${error.message}`);
    
    return res.status(500).json({
      status: 'error',
      message: 'Error checking RAG status',
      error: error.message
    });
  }
};