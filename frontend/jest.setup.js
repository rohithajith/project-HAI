// Jest setup file for frontend testing

// Mock Socket.IO client
jest.mock('socket.io-client', () => {
    return {
        __esModule: true,
        default: jest.fn(() => ({
            on: jest.fn(),
            emit: jest.fn(),
            connect: jest.fn(),
            disconnect: jest.fn(),
            connected: true
        }))
    };
});

// Mock browser APIs and global objects
Object.defineProperty(window, 'localStorage', {
    value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
    },
    writable: true
});

// Mock console methods to prevent cluttering test output
console.warn = jest.fn();
console.error = jest.fn();
console.log = jest.fn();

// Add any global test setup or mocking here
beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
});

// Polyfill for requestAnimationFrame
global.requestAnimationFrame = (cb) => setTimeout(cb, 0);

// Add any custom matchers or extensions
expect.extend({
    toBeValidWebSocketMessage(received) {
        const pass = received && 
            typeof received === 'object' && 
            (received.type || received.data);
        
        if (pass) {
            return {
                message: () => `expected ${received} to be a valid WebSocket message`,
                pass: true
            };
        } else {
            return {
                message: () => `expected a valid WebSocket message, got ${received}`,
                pass: false
            };
        }
    }
});