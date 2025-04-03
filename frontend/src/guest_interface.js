// Enhanced Guest Interface for Hotel AI System

import WebSocketClient from './websocket_client.js';
import NotificationService from './notification_service.js';

class GuestInterface {
    constructor() {
        this.webSocketClient = null;
        this.roomNumber = null;
        this.messageHistory = [];
        this.notificationHistory = [];
        this.initializeInterface();
    }

    initializeInterface() {
        this.createChatbotLayout();
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupNotificationHandlers();
    }

    createChatbotLayout() {
        const chatbotContainer = document.createElement('div');
        chatbotContainer.id = 'guest-chatbot';
        chatbotContainer.innerHTML = `
            <div class="chatbot-header">
                <h1>Hotel AI Guest Assistant</h1>
                <div id="connection-status" class="status-indicator"></div>
            </div>
            
            <div class="room-validation">
                <label for="room-number">Your Room Number:</label>
                <input type="text" id="room-number" placeholder="Enter room number" required>
                <div id="room-error" class="error-message"></div>
            </div>
            
            <div class="chatbox" id="chatbox">
                <div class="message-container" id="message-container">
                    <div class="message bot welcome-message">
                        Welcome to Hotel AI! Please enter your room number to begin.
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <input 
                    type="text" 
                    id="message-input" 
                    placeholder="Type your message..." 
                    disabled
                >
                <button id="send-button" disabled>Send</button>
            </div>
            
            <div class="notifications-panel">
                <h2>Notifications</h2>
                <div id="notifications-container"></div>
            </div>
        `;
        document.body.appendChild(chatbotContainer);
    }

    setupWebSocket() {
        this.webSocketClient = new WebSocketClient('guest', this.getBackendUrl());
        
        this.webSocketClient.on('connect', () => {
            this.updateConnectionStatus(true);
        });

        this.webSocketClient.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });

        this.webSocketClient.on('message', this.handleIncomingMessage.bind(this));
        this.webSocketClient.on('notification', this.handleNotification.bind(this));
        this.webSocketClient.on('connectionFailed', this.handleConnectionFailure.bind(this));

        this.webSocketClient.connect();
    }

    setupEventListeners() {
        const roomNumberInput = document.getElementById('room-number');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const roomError = document.getElementById('room-error');

        roomNumberInput.addEventListener('input', () => {
            const roomNumber = roomNumberInput.value.trim();
            const isValid = this.validateRoomNumber(roomNumber);
            
            roomError.textContent = isValid ? '' : 'Please enter a valid room number';
            roomError.style.display = isValid ? 'none' : 'block';
            
            if (isValid) {
                messageInput.disabled = false;
                sendButton.disabled = false;
                this.roomNumber = roomNumber;
            } else {
                messageInput.disabled = true;
                sendButton.disabled = true;
            }
        });

        sendButton.addEventListener('click', this.sendMessage.bind(this));
        messageInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    setupNotificationHandlers() {
        NotificationService.on('add', this.renderNotifications.bind(this));
    }

    validateRoomNumber(roomNumber) {
        // Validate room number: 3-digit number
        return /^[1-9]\d{2}$/.test(roomNumber);
    }

    sendMessage() {
        const messageInput = document.getElementById('message-input');
        const messageText = messageInput.value.trim();

        if (messageText && this.roomNumber) {
            this.addMessageToChatbox(messageText, 'user');
            
            const messageToSend = `I am in room ${this.roomNumber}. ${messageText}`;

            this.messageHistory.push({
                role: 'user',
                content: messageToSend
            });

            this.webSocketClient.emit('message', {
                message: messageToSend,
                room: this.roomNumber,
                history: this.messageHistory
            });

            messageInput.value = '';
        }
    }

    handleIncomingMessage(data) {
        if (data.response) {
            this.addMessageToChatbox(data.response, 'bot');
            
            this.messageHistory.push({
                role: 'assistant',
                content: data.response
            });
        }
    }

    handleNotification(notification) {
        // Validate and add notification
        if (NotificationService.add(notification)) {
            this.notificationHistory.push(notification);
            this.renderNotifications();
        }
    }

    handleConnectionFailure(error) {
        this.addMessageToChatbox('Connection error. Please try again later.', 'bot');
        this.updateConnectionStatus(false);
    }

    addMessageToChatbox(text, sender) {
        const messageContainer = document.getElementById('message-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;
        messageContainer.appendChild(messageDiv);

        // Auto-scroll to bottom
        const chatbox = document.getElementById('chatbox');
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    renderNotifications() {
        const notificationsContainer = document.getElementById('notifications-container');
        const notifications = NotificationService.getAll();
        
        // Filter notifications for current room
        const roomNotifications = this.roomNumber 
            ? notifications.filter(n => n.room_number === this.roomNumber)
            : notifications;

        notificationsContainer.innerHTML = roomNotifications.map(notification => `
            <div class="notification ${notification.priority}">
                <span class="notification-type">${notification.type}</span>
                <span class="notification-message">${notification.message || 'New notification'}</span>
                <span class="notification-time">${this.formatTime(notification.timestamp)}</span>
            </div>
        `).join('');
    }

    updateConnectionStatus(isConnected) {
        const statusIndicator = document.getElementById('connection-status');
        statusIndicator.textContent = isConnected ? 'Connected' : 'Disconnected';
        statusIndicator.className = `status-indicator ${isConnected ? 'connected' : 'disconnected'}`;
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    getBackendUrl() {
        // Get backend URL from environment or configuration
        return process.env.BACKEND_URL || 'http://localhost:5000';
    }
}

export default new GuestInterface();