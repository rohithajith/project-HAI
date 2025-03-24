/**
 * Tests for the hotel information controller.
 */

const { expect } = require('chai');
const sinon = require('sinon');
const { spawn } = require('child_process');
const EventEmitter = require('events');
const hotelInfoController = require('../../controllers/hotelInfoController');

describe('Hotel Info Controller', () => {
  let req, res, next, spawnStub, processStub;

  beforeEach(() => {
    // Mock request, response, and next function
    req = {
      body: {
        message: 'What are the room amenities?',
        history: [
          { role: 'user', content: 'Hello' },
          { role: 'system', content: 'How can I help you?' }
        ],
        guestName: 'John Doe',
        bookingId: 'B12345',
        queryType: 'rooms'
      }
    };
    
    res = {
      status: sinon.stub().returnsThis(),
      json: sinon.stub()
    };
    
    next = sinon.stub();
    
    // Create a mock process
    processStub = new EventEmitter();
    processStub.stdout = new EventEmitter();
    processStub.stderr = new EventEmitter();
    processStub.kill = sinon.stub();
    
    // Stub the spawn function
    spawnStub = sinon.stub(require('child_process'), 'spawn').returns(processStub);
  });
  
  afterEach(() => {
    // Restore stubs
    sinon.restore();
  });
  
  describe('queryHotelInfo', () => {
    it('should return a successful response when the agent returns valid data', async () => {
      // Mock the agent response
      const agentResponse = {
        response: 'All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi.',
        suggested_actions: ['View room types', 'Book a room', 'Request amenities'],
        related_info: {
          category: 'rooms',
          highlights: [
            {
              category: 'rooms',
              content: 'All rooms feature air conditioning, flat-screen TVs, and free Wi-Fi.'
            }
          ]
        }
      };
      
      // Set up the process to emit the agent response
      setTimeout(() => {
        processStub.stdout.emit('data', Buffer.from(JSON.stringify(agentResponse)));
        processStub.emit('close', 0);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.queryHotelInfo(req, res, next);
      
      // Check that spawn was called with the correct arguments
      expect(spawnStub.calledOnce).to.be.true;
      expect(spawnStub.firstCall.args[0]).to.equal('python');
      expect(spawnStub.firstCall.args[1][0]).to.equal('-m');
      expect(spawnStub.firstCall.args[1][1]).to.equal('run');
      expect(spawnStub.firstCall.args[1][2]).to.equal('--agent');
      expect(spawnStub.firstCall.args[1][3]).to.equal('hotel_info');
      
      // Check that the response was sent correctly
      expect(res.status.calledWith(200)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'success',
        data: agentResponse
      });
    });
    
    it('should return an error response when the agent returns an error', async () => {
      // Set up the process to emit an error
      setTimeout(() => {
        processStub.stderr.emit('data', Buffer.from('Error processing message'));
        processStub.emit('close', 1);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.queryHotelInfo(req, res, next);
      
      // Check that the error response was sent correctly
      expect(res.status.calledWith(500)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'error',
        message: 'Error processing hotel information query'
      });
    });
    
    it('should return an error response when the agent returns invalid JSON', async () => {
      // Set up the process to emit invalid JSON
      setTimeout(() => {
        processStub.stdout.emit('data', Buffer.from('Not valid JSON'));
        processStub.emit('close', 0);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.queryHotelInfo(req, res, next);
      
      // Check that the error response was sent correctly
      expect(res.status.calledWith(500)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'error',
        message: 'Error parsing agent response'
      });
    });
    
    it('should handle missing request body fields', async () => {
      // Remove required fields from the request
      req.body = {
        message: 'What are the room amenities?'
      };
      
      // Call the controller function
      await hotelInfoController.queryHotelInfo(req, res, next);
      
      // Check that the error response was sent correctly
      expect(res.status.calledWith(400)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'error',
        message: 'Missing required fields'
      });
    });
  });
  
  describe('initRAG', () => {
    it('should return a successful response when RAG initialization succeeds', async () => {
      // Set up the process to emit a success message
      setTimeout(() => {
        processStub.stdout.emit('data', Buffer.from('RAG initialized successfully'));
        processStub.emit('close', 0);
      }, 10);
      
      // Set up the request with query parameters
      req.query = { clear: 'true' };
      
      // Call the controller function
      await hotelInfoController.initRAG(req, res, next);
      
      // Check that spawn was called with the correct arguments
      expect(spawnStub.calledOnce).to.be.true;
      expect(spawnStub.firstCall.args[0]).to.equal('python');
      expect(spawnStub.firstCall.args[1][0]).to.equal('-m');
      expect(spawnStub.firstCall.args[1][1]).to.equal('rag.init_rag');
      expect(spawnStub.firstCall.args[1][2]).to.equal('--clear');
      
      // Check that the response was sent correctly
      expect(res.status.calledWith(200)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'success',
        message: 'RAG module initialized successfully'
      });
    });
    
    it('should return an error response when RAG initialization fails', async () => {
      // Set up the process to emit an error
      setTimeout(() => {
        processStub.stderr.emit('data', Buffer.from('Error initializing RAG'));
        processStub.emit('close', 1);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.initRAG(req, res, next);
      
      // Check that the error response was sent correctly
      expect(res.status.calledWith(500)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'error',
        message: 'Error initializing RAG module'
      });
    });
  });
  
  describe('getRAGStatus', () => {
    it('should return a successful response with RAG status', async () => {
      // Mock the agent response
      const statusResponse = {
        initialized: true,
        document_count: 25,
        embedding_dimension: 768,
        categories: {
          rooms: 5,
          dining: 4,
          spa: 3,
          facilities: 4,
          policies: 6,
          general: 3
        }
      };
      
      // Set up the process to emit the status response
      setTimeout(() => {
        processStub.stdout.emit('data', Buffer.from(JSON.stringify(statusResponse)));
        processStub.emit('close', 0);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.getRAGStatus(req, res, next);
      
      // Check that spawn was called with the correct arguments
      expect(spawnStub.calledOnce).to.be.true;
      expect(spawnStub.firstCall.args[0]).to.equal('python');
      expect(spawnStub.firstCall.args[1][0]).to.equal('-m');
      expect(spawnStub.firstCall.args[1][1]).to.equal('run');
      expect(spawnStub.firstCall.args[1][2]).to.equal('--agent');
      expect(spawnStub.firstCall.args[1][3]).to.equal('rag_status');
      
      // Check that the response was sent correctly
      expect(res.status.calledWith(200)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'success',
        data: statusResponse
      });
    });
    
    it('should return an error response when getting RAG status fails', async () => {
      // Set up the process to emit an error
      setTimeout(() => {
        processStub.stderr.emit('data', Buffer.from('Error getting RAG status'));
        processStub.emit('close', 1);
      }, 10);
      
      // Call the controller function
      await hotelInfoController.getRAGStatus(req, res, next);
      
      // Check that the error response was sent correctly
      expect(res.status.calledWith(500)).to.be.true;
      expect(res.json.calledOnce).to.be.true;
      expect(res.json.firstCall.args[0]).to.deep.include({
        status: 'error',
        message: 'Error getting RAG status'
      });
    });
  });
});