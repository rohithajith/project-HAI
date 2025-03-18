const express = require('express');
const chatbotController = require('../controllers/chatbotController_postgres');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Public route for processing chatbot messages (works with or without authentication)
router.post('/', chatbotController.processMessage);

// Protected routes (require authentication)
router.post('/consent', protect, chatbotController.updateConsent);
router.get('/history', protect, chatbotController.getConversationHistory);
router.delete('/history/:sessionId?', protect, chatbotController.deleteConversationHistory);

module.exports = router;