const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const WebSocket = require('ws');
const AgentManager = require('./ai_agents/agentManager');
const notificationService = require('./services/notificationService');

// Configuration
const SERVER_URL = 'http://localhost:5000';
const WS_URL = 'ws://localhost:5000';
const TEST_ROOM = '304';

// Test cases
const TEST_CASES = [
  // Server connection tests
  {
    name: "Server Health Check",
    type: "connection",
    endpoint: "/health"
  },
  {
    name: "WebSocket Connection", 
    type: "websocket"  
  },
  // Room Service Agent tests
  {
    name: "Room Service - Food Order",
    type: "agent",
    message: "I'd like to order room service - 2 burgers and fries",
    expected: {
      agent: "RoomServiceAgent",
      toolUsed: true,
      toolName: "order_food"
    }
  },
  // Maintenance Agent tests
  {
    name: "Maintenance - Urgent Issue",
    type: "agent",
    message: "EMERGENCY! My toilet is overflowing!",
    expected: {
      agent: "MaintenanceAgent", 
      toolUsed: true,
      toolName: "report_issue",
      urgency: "emergency"
    }
  },
  // Local Model Fallback tests
  {
    name: "General Question",
    type: "agent",
    message: "What time is checkout?",
    expected: {
      agent: null,
      toolUsed: false,
      processedBy: "model"
    }
  }
];

// Test runner
async function runTests() {
  const results = [];
  
  // 1. Test server connections
  console.log("\n=== Testing Server Connections ===");
  for (const testCase of TEST_CASES.filter(t => t.type === 'connection')) {
    const result = await testConnection(testCase);
    results.push(result);
    console.log(`${testCase.name}: ${result.passed ? 'PASSED' : 'FAILED'}`);
  }

  // 2. Test WebSocket
  console.log("\n=== Testing WebSocket ===");
  const wsResult = await testWebSocket();
  results.push(wsResult);
  console.log(`WebSocket: ${wsResult.passed ? 'PASSED' : 'FAILED'}`);

  // 3. Test agent flows
  console.log("\n=== Testing Agent Flows ===");
  for (const testCase of TEST_CASES.filter(t => t.type === 'agent')) {
    const result = await testAgentFlow(testCase);
    results.push(result);
    console.log(`${testCase.name}: ${result.passed ? 'PASSED' : 'FAILED'}`);
  }

  // Save results
  fs.writeFileSync('test_results.json', JSON.stringify(results, null, 2));
  console.log('\nAll tests completed. Results saved to test_results.json');
}

// Connection test
async function testConnection(testCase) {
  try {
    const response = await axios.get(`${SERVER_URL}${testCase.endpoint}`);
    return {
      test: testCase.name,
      status: response.status,
      passed: response.status === 200
    };
  } catch (error) {
    return {
      test: testCase.name,
      error: error.message,
      passed: false
    };
  }
}

// WebSocket test
async function testWebSocket() {
  return new Promise((resolve) => {
    const result = { test: "WebSocket Connection" };
    const ws = new WebSocket(WS_URL);

    ws.on('open', () => {
      result.connected = true;
      ws.send(JSON.stringify({
        type: 'test_notification',
        room: TEST_ROOM
      }));

      setTimeout(() => {
        ws.close();
        result.passed = result.receivedNotification;
        resolve(result);
      }, 1000);
    });

    ws.on('message', (data) => {
      const msg = JSON.parse(data);
      if (msg.type === 'notification') {
        result.receivedNotification = true;
      }
    });

    ws.on('error', (error) => {
      result.error = error.message;
      result.passed = false;
      resolve(result);
    });
  });
}

// Agent flow test
async function testAgentFlow(testCase) {
  const history = [
    { role: 'user', content: `I am in room ${TEST_ROOM}` },
    { role: 'assistant', content: 'How can I assist you today?' }
  ];

  // Process through agent system
  const agentManager = new AgentManager();
  const agentResult = await agentManager.process(testCase.message, history);
  
  // Get model response if needed
  let modelResponse = null;
  if (!agentResult.response && !agentResult.toolUsed) {
    modelResponse = await getModelResponse(testCase.message, history);
  }

  // Validate result
  const passed = validateResult(testCase.expected, {
    agent: agentResult.response ? agentResult.agentName : null,
    toolUsed: agentResult.toolUsed || false,
    toolName: agentResult.toolName || null,
    response: agentResult.response || modelResponse,
    notifications: agentResult.notifications || []
  });

  return {
    test: testCase.name,
    input: testCase.message,
    actual: {
      agent: agentResult.response ? agentResult.agentName : null,
      toolUsed: agentResult.toolUsed,
      response: agentResult.response || modelResponse
    },
    passed
  };
}

// Helper functions
function getModelResponse(message, history) {
  const historyJson = JSON.stringify(history);
  const scriptPath = path.join(__dirname, 'local_model_chatbot.py');
  
  try {
    const stdout = execSync(
      `python "${scriptPath}" --message "${message.replace(/"/g, '\\"')}" --history "${historyJson.replace(/"/g, '\\"')}"`
    ).toString();
    return JSON.parse(stdout).response;
  } catch (error) {
    return { error: 'Model response failed' };
  }
}

function validateResult(expected, actual) {
  if (expected.agent !== actual.agent) return false;
  if (expected.toolUsed !== actual.toolUsed) return false;
  if (expected.toolName && expected.toolName !== actual.toolName) return false;
  if (expected.urgency && !actual.notifications.some(n => n.urgency === expected.urgency)) return false;
  if (!expected.agent && !actual.response) return false;
  return true;
}

// Run tests
runTests().catch(console.error);