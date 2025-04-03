import WebSocketClient from '../src/websocket_client';
import io from 'socket.io-client';

// Mock socket.io-client
jest.mock('socket.io-client');

describe('WebSocketClient', () => {
    let webSocketClient;
    let mockSocket;

    beforeEach(() => {
        // Create a mock socket
        mockSocket = {
            on: jest.fn(),
            emit: jest.fn(),
            connect: jest.fn(),
            disconnect: jest.fn(),
            connected: true
        };

        // Mock io.connect to return our mock socket
        io.mockReturnValue(mockSocket);

        // Create a new WebSocketClient instance
        webSocketClient = new WebSocketClient('test-namespace', 'http://localhost:5000');
    });

    test('constructor initializes correctly', () => {
        expect(webSocketClient.namespace).toBe('test-namespace');
        expect(webSocketClient.backendUrl).toBe('http://localhost:5000');
        expect(webSocketClient.socket).toBeNull();
        expect(webSocketClient.listeners).toEqual({});
    });

    test('connect method establishes socket connection', () => {
        webSocketClient.connect();

        expect(io).toHaveBeenCalledWith('http://localhost:5000', {
            path: '/test-namespace',
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000
        });
    });

    test('on method registers event listeners', () => {
        const mockCallback = jest.fn();
        webSocketClient.on('testEvent', mockCallback);

        expect(webSocketClient.listeners['testEvent']).toContain(mockCallback);
    });

    test('emit method sends messages when connected', () => {
        webSocketClient.socket = mockSocket;
        webSocketClient.emit('testEvent', { data: 'test' });

        expect(mockSocket.emit).toHaveBeenCalledWith('testEvent', { data: 'test' });
    });

    test('emit method does not send messages when not connected', () => {
        webSocketClient.socket = null;
        const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
        
        webSocketClient.emit('testEvent', { data: 'test' });

        expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Cannot emit'));
        consoleSpy.mockRestore();
    });

    test('disconnect method closes socket connection', () => {
        webSocketClient.socket = mockSocket;
        webSocketClient.disconnect();

        expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    test('triggerListener calls registered callbacks', () => {
        const mockCallback1 = jest.fn();
        const mockCallback2 = jest.fn();
        
        webSocketClient.on('testEvent', mockCallback1);
        webSocketClient.on('testEvent', mockCallback2);
        
        webSocketClient.triggerListener('testEvent', { data: 'test' });

        expect(mockCallback1).toHaveBeenCalledWith({ data: 'test' });
        expect(mockCallback2).toHaveBeenCalledWith({ data: 'test' });
    });
});