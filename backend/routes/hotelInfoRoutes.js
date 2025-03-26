/**
 * Hotel Information Routes
 * 
 * Routes for hotel information retrieval using the RAG-enabled hotel information agent.
 */

const express = require('express');
const hotelInfoController = require('../controllers/hotelInfoController');
const authMiddleware = require('../middleware/authMiddleware');

const router = express.Router();

// Get hotel information (query endpoint)
router.post('/query', hotelInfoController.getHotelInfo);
router.get('/query', hotelInfoController.getHotelInfo);

// Initialize RAG module (admin only)
router.post('/init-rag', authMiddleware.protect, authMiddleware.restrictTo('admin'), hotelInfoController.initializeRag);

// Get RAG status
router.get('/rag-status', hotelInfoController.getRagStatus);

// Handle towel requests
router.post('/towel-request', hotelInfoController.handleTowelRequest);

// Get room data
router.get('/room-data', hotelInfoController.getRoomData);

// Handle chat requests
router.post('/chat', hotelInfoController.handleChat);

module.exports = router;