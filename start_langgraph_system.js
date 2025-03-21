/**
 * Start script for the Hotel AI Assistant with LangGraph multi-agent system.
 * 
 * This script starts both the Node.js backend and the Python FastAPI server.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Configuration
const NODE_ENV = process.env.NODE_ENV || 'development';
const NODE_PORT = process.env.PORT || 5000;
const PYTHON_PORT = process.env.PYTHON_PORT || 8000;
const PYTHON_HOST = process.env.PYTHON_HOST || '0.0.0.0';
const PYTHON_DEBUG = process.env.PYTHON_DEBUG === 'true';

// Paths
const BACKEND_DIR = path.join(__dirname, 'backend');
const AI_AGENTS_DIR = path.join(BACKEND_DIR, 'ai_agents');
const NODE_APP_PATH = path.join(BACKEND_DIR, 'server_langgraph.js');
const PYTHON_APP_PATH = path.join(AI_AGENTS_DIR, 'run.py');

// Check if the required files exist
if (!fs.existsSync(AI_AGENTS_DIR)) {
  console.error(`Error: AI agents directory not found at ${AI_AGENTS_DIR}`);
  process.exit(1);
}

if (!fs.existsSync(PYTHON_APP_PATH)) {
  console.error(`Error: Python app not found at ${PYTHON_APP_PATH}`);
  process.exit(1);
}

// Create a server.js file for the Node.js backend if it doesn't exist
if (!fs.existsSync(NODE_APP_PATH)) {
  const serverContent = `
const app = require('./app_langgraph');
const http = require('http');
const socketIo = require('socket.io');
const socketService = require('./services/socketService');

// Set port
const port = process.env.PORT || 5000;

// Create HTTP server
const server = http.createServer(app);

// Initialize Socket.IO
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Initialize socket service
socketService.initialize(io);

// Start server
server.listen(port, () => {
  console.log(\`Server running on port \${port}\`);
});
  `;
  
  fs.writeFileSync(NODE_APP_PATH, serverContent);
  console.log(`Created Node.js server file at ${NODE_APP_PATH}`);
}

// Create a .env file for the Python FastAPI server if it doesn't exist
const pythonEnvPath = path.join(AI_AGENTS_DIR, '.env');
if (!fs.existsSync(pythonEnvPath)) {
  const envContent = fs.readFileSync(path.join(AI_AGENTS_DIR, '.env.example'), 'utf8');
  fs.writeFileSync(pythonEnvPath, envContent);
  console.log(`Created Python .env file at ${pythonEnvPath}`);
}

// Function to start a process and handle its output
function startProcess(command, args, options, name) {
  console.log(`Starting ${name}...`);
  
  const process = spawn(command, args, options);
  
  process.stdout.on('data', (data) => {
    console.log(`[${name}] ${data.toString().trim()}`);
  });
  
  process.stderr.on('data', (data) => {
    console.error(`[${name}] ${data.toString().trim()}`);
  });
  
  process.on('close', (code) => {
    console.log(`[${name}] Process exited with code ${code}`);
    
    if (code !== 0) {
      console.error(`[${name}] Process crashed. Restarting in 5 seconds...`);
      setTimeout(() => {
        startProcess(command, args, options, name);
      }, 5000);
    }
  });
  
  return process;
}

// Start the Python FastAPI server
const pythonProcess = startProcess(
  'python',
  [PYTHON_APP_PATH],
  {
    env: {
      ...process.env,
      PORT: PYTHON_PORT,
      HOST: PYTHON_HOST,
      DEBUG: PYTHON_DEBUG.toString()
    },
    cwd: AI_AGENTS_DIR
  },
  'Python FastAPI'
);

// Start the Node.js backend
const nodeProcess = startProcess(
  'node',
  [NODE_APP_PATH],
  {
    env: {
      ...process.env,
      PORT: NODE_PORT,
      USE_LANGGRAPH_CHATBOT: 'true',
      AI_ASSISTANT_API_URL: `http://localhost:${PYTHON_PORT}`
    },
    cwd: BACKEND_DIR
  },
  'Node.js Backend'
);

// Handle process termination
process.on('SIGINT', () => {
  console.log('Shutting down...');
  
  // Kill the Python process
  if (pythonProcess) {
    pythonProcess.kill();
  }
  
  // Kill the Node.js process
  if (nodeProcess) {
    nodeProcess.kill();
  }
  
  process.exit(0);
});

console.log(`
🚀 Hotel AI Assistant with LangGraph multi-agent system is starting up!

📡 Node.js Backend: http://localhost:${NODE_PORT}
🤖 Python FastAPI: http://localhost:${PYTHON_PORT}

Press Ctrl+C to stop all services.
`);