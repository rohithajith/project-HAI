const express = require('express');
const router = express.Router();
const chatbotController = require('../controllers/chatbotController');

// Route to process chatbot messages
router.post('/', chatbotController.processMessage);

module.exports = router;