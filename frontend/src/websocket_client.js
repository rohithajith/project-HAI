// Enhanced WebSocket Client for Hotel AI System

class WebSocketClient {
    constructor(namespace, backendUrl) {
        this.namespace = namespace;
        this.backendUrl = backendUrl;
        this.socket = null;
        this.listeners = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.requestTimeout = 5000; // 5 seconds timeout
    }

    connect() {
        try {
            this.socket = io(this.backendUrl, {
                path: `/${this.namespace}`,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                timeout: this.requestTimeout
            });

            this.setupEventHandlers();
        } catch (error) {
            console.error(`WebSocket connection error for ${this.namespace}:`, error);
            this.handleConnectionError(error);
        }
    }

    setupEventHandlers() {
        if (!this.socket) return;

        this.socket.on('connect', () => {
            console.log(`Connected to ${this.namespace} namespace`);
            this.reconnectAttempts = 0;
            this.triggerListener('connect');
        });

        this.socket.on('disconnect', (reason) => {
            console.warn(`Disconnected from ${this.namespace} namespace: ${reason}`);
            this.triggerListener('disconnect', reason);
        });

        this.socket.on('connect_error', (error) => {
            console.error(`Connection error for ${this.namespace}:`, error);
            this.handleConnectionError(error);
        });

        this.socket.on('message', (data) => {
            this.processMessage(data);
        });

        this.socket.on('notification', (notification) => {
            this.processNotification(notification);
        });
    }

    processMessage(data) {
        // Enhanced message processing with timeout handling
        const processedData = this.transformMessageData(data);
        this.triggerListener('message', processedData);
    }

    processNotification(notification) {
        // Validate notification structure
        if (this.validateNotification(notification)) {
            this.triggerListener('notification', notification);
        }
    }

    transformMessageData(data) {
        // Transform incoming message to ensure consistent structure
        return {
            ...data,
            timestamp: new Date().toISOString(),
            processed: true
        };
    }

    validateNotification(notification) {
        const requiredFields = ['type', 'agent', 'room_number'];
        return requiredFields.every(field => 
            notification.hasOwnProperty(field) && 
            notification[field] !== null && 
            notification[field] !== undefined
        );
    }

    handleConnectionError(error) {
        this.reconnectAttempts++;
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error(`Max reconnection attempts reached for ${this.namespace}`);
            this.triggerListener('connectionFailed', error);
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    triggerListener(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    emit(event, data) {
        if (this.socket && this.socket.connected) {
            // Add timeout handling for emissions
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Emission timeout')), this.requestTimeout)
            );

            const emitPromise = new Promise(resolve => 
                this.socket.emit(event, data, resolve)
            );

            Promise.race([emitPromise, timeoutPromise])
                .catch(error => {
                    console.warn(`WebSocket emission error: ${error.message}`);
                    this.triggerListener('emissionError', error);
                });
        } else {
            console.warn(`Cannot emit ${event}: Socket not connected`);
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

export default WebSocketClient;