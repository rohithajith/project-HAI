const express = require('express');
const router = express.Router();
const chatbotController = require('../controllers/chatbotController_langgraph');

// Route to process chatbot messages
router.post('/', chatbotController.processMessage);

// Route to get conversation history
router.get('/conversations/:conversation_id', chatbotController.getConversation);

// Route to delete a conversation
router.delete('/conversations/:conversation_id', chatbotController.deleteConversation);

// Route to check the health of the AI Assistant API
router.get('/health', chatbotController.healthCheck);

module.exports = router;