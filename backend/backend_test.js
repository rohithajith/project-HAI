const axios = require('axios');
const io = require('socket.io-client');

// --- Configuration ---
const BACKEND_URL = 'http://localhost:5000'; // Adjust if your backend runs on a different port
const API_ENDPOINT = `${BACKEND_URL}/api/chatbot`;
const SOCKET_TIMEOUT = 3000; // Max time (ms) to wait for socket events after sending a message

// --- Test Cases ---
// Each test case includes:
// - description: What the test is checking
// - message: The message to send to the chatbot API
// - history: Optional conversation history
// - expectedEvents: An array of WebSocket event names expected to be triggered
const testCases = [
  {
    description: 'Trigger Room Service (Food)',
    message: 'I want to order a burger and fries to room 101.',
    history: [{ role: 'user', content: 'I am in room 101.' }],
    expectedEvents: ['room_service_food'],
  },
  {
    description: 'Trigger Room Service (Drink)',
    message: 'Can I get a coke with light ice?',
    history: [{ role: 'user', content: 'I am in room 101.' }, { role: 'assistant', content: 'Sure, anything else?' }],
    expectedEvents: ['room_service_drink'],
  },
  {
    description: 'Trigger Maintenance (Report Issue)',
    message: 'The shower in room 202 is broken, it is leaking!',
    history: [{ role: 'user', content: 'I am in room 202.' }],
    expectedEvents: ['maintenance_report'],
  },
  {
    description: 'Trigger Maintenance (Schedule)',
    message: 'Please schedule someone to clean the AC filter in room 305 tomorrow afternoon.',
    history: [{ role: 'user', content: 'I am in room 305.' }],
    expectedEvents: ['maintenance_schedule'],
  },
  {
    description: 'No Agent Trigger (Fallback to LLM)',
    message: 'What time does the hotel restaurant open?',
    history: [],
    expectedEvents: [], // No agent should handle this, so no specific notifications expected
  },
  {
    description: 'Room Service (Food) - Different Room',
    message: 'Send a club sandwich to room 410.',
    history: [{ role: 'user', content: 'I am in room 410.' }],
    expectedEvents: ['room_service_food'],
  },
];

// --- Test Runner ---
async function runTests() {
  console.log(`--- Starting Backend Agent Test ---`);
  console.log(`Connecting to WebSocket server at ${BACKEND_URL}...`);

  const socket = io(BACKEND_URL, {
    reconnection: false, // Don't automatically reconnect for testing
    timeout: 2000,
  });

  let connected = false;
  const receivedEvents = {}; // Store received events for each test case

  socket.on('connect', () => {
    connected = true;
    console.log('WebSocket connected successfully.');
  });

  socket.on('connect_error', (err) => {
    console.error(`WebSocket connection error: ${err.message}`);
    connected = false;
  });

  socket.on('disconnect', (reason) => {
    console.log(`WebSocket disconnected: ${reason}`);
    connected = false;
  });

  // Generic listener to capture all expected events
  const allExpectedEvents = [...new Set(testCases.flatMap(tc => tc.expectedEvents))];
  allExpectedEvents.forEach(eventName => {
    socket.on(eventName, (payload) => {
      console.log(`[SOCKET RECV] Event: ${eventName}, Payload:`, JSON.stringify(payload));
      if (!receivedEvents[eventName]) {
        receivedEvents[eventName] = [];
      }
      receivedEvents[eventName].push(payload);
    });
  });

  // Wait briefly for connection
  await new Promise(resolve => setTimeout(resolve, 1000));

  if (!connected) {
    console.error('Failed to connect to WebSocket server. Aborting tests.');
    process.exit(1);
  }

  let allTestsPassed = true;

  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i];
    console.log(`\n--- Running Test ${i + 1}: ${testCase.description} ---`);
    console.log(`Sending message: "${testCase.message}"`);

    // Clear received events for this test
    Object.keys(receivedEvents).forEach(key => { receivedEvents[key] = []; });
    let testPassed = true;

    try {
      const response = await axios.post(API_ENDPOINT, {
        message: testCase.message,
        history: testCase.history || [],
      });

      console.log(`[HTTP RESP ${response.status}] Response: "${response.data?.response}"`);

      // Wait for socket events to potentially arrive
      await new Promise(resolve => setTimeout(resolve, SOCKET_TIMEOUT));

      // Verify expected events
      if (testCase.expectedEvents.length > 0) {
        for (const expectedEvent of testCase.expectedEvents) {
          if (!receivedEvents[expectedEvent] || receivedEvents[expectedEvent].length === 0) {
            console.error(`[FAIL] Expected WebSocket event "${expectedEvent}" was NOT received.`);
            testPassed = false;
          } else {
            console.log(`[PASS] Received expected WebSocket event "${expectedEvent}".`);
            // Optionally add payload validation here
          }
        }
      } else {
         // Check if any *unexpected* agent events were received
         const unexpectedReceived = Object.keys(receivedEvents).filter(key => receivedEvents[key].length > 0);
         if (unexpectedReceived.length > 0) {
             console.warn(`[WARN] Expected no agent events, but received: ${unexpectedReceived.join(', ')}`);
             // Decide if this should be a failure based on strictness
             // testPassed = false;
         } else {
             console.log(`[PASS] Correctly received no specific agent events.`);
         }
      }

    } catch (error) {
      console.error(`[FAIL] Error during API call: ${error.response?.status || error.message}`);
      if (error.response?.data) {
        console.error('Error data:', error.response.data);
      }
      testPassed = false;
    }

    if (!testPassed) {
      allTestsPassed = false;
    }
    console.log(`--- Test ${i + 1} ${testPassed ? 'PASSED' : 'FAILED'} ---`);
  }

  console.log('\n--- Test Summary ---');
  console.log(`Overall Result: ${allTestsPassed ? 'All tests passed!' : 'Some tests FAILED.'}`);

  socket.disconnect();
  process.exit(allTestsPassed ? 0 : 1); // Exit with code 0 on success, 1 on failure
}

runTests();