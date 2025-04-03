import io from 'socket.io-client';

class WebSocketService {
    constructor() {
        this.socket = null;
        this.listeners = {
            'room_service_dashboard': [],
            'admin_dashboard': []
        };
    }

    connect() {
        // Connect to the WebSocket server
        this.socket = io('http://localhost:5001');

        // Handle connection
        this.socket.on('connect', () => {
            console.log('Connected to Agent Update WebSocket');
        });

        // Handle agent updates
        this.socket.on('agent_update', (data) => {
            console.log('Agent Update Received:', data);
            this._processAgentUpdate(data);
        });

        // Handle connection errors
        this.socket.on('connect_error', (error) => {
            console.error('WebSocket Connection Error:', error);
        });
    }

    _processAgentUpdate(updateData) {
        const { component, action, message, details } = updateData;

        // Route updates to specific dashboard listeners
        switch(component) {
            case 'room_service_dashboard':
                this._notifyListeners('room_service_dashboard', { action, message, details });
                break;
            case 'admin_dashboard':
                this._notifyListeners('admin_dashboard', { action, message, details });
                break;
            default:
                console.warn('Unhandled dashboard update:', updateData);
        }
    }

    addListener(dashboard, callback) {
        if (this.listeners[dashboard]) {
            this.listeners[dashboard].push(callback);
        } else {
            console.warn(`No listeners defined for dashboard: ${dashboard}`);
        }
    }

    _notifyListeners(dashboard, updateData) {
        if (this.listeners[dashboard]) {
            this.listeners[dashboard].forEach(callback => {
                try {
                    callback(updateData);
                } catch (error) {
                    console.error(`Error in ${dashboard} listener:`, error);
                }
            });
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Singleton instance
export default new WebSocketService();