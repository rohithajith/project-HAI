/**
 * Hotel Information Routes
 * 
 * Routes for hotel information retrieval using the RAG-enabled hotel information agent.
 */

const express = require('express');
const hotelInfoController = require('../controllers/hotelInfoController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

// Get hotel information
router.post('/query', hotelInfoController.getHotelInfo);

// Initialize RAG module (admin only)
router.post('/init-rag', authMiddleware.protect, authMiddleware.restrictTo('admin'), hotelInfoController.initializeRag);

// Get RAG status
router.get('/rag-status', hotelInfoController.getRagStatus);

module.exports = router;