// Combined Admin and Room Service Dashboard

import WebSocketClient from './websocket_client.js';
import NotificationService from './notification_service.js';

class CombinedDashboard {
    constructor() {
        this.webSocketClient = null;
        this.currentUser = null;
        this.initializeDashboard();
    }

    initializeDashboard() {
        this.setupWebSocket();
        this.setupNotificationHandlers();
        this.setupUserInterface();
        this.setupEventListeners();
    }

    setupWebSocket() {
        // Use a shared namespace for admin and room service
        this.webSocketClient = new WebSocketClient('admin-room-service', this.getBackendUrl());
        
        this.webSocketClient.on('connect', () => {
            this.updateConnectionStatus(true);
        });

        this.webSocketClient.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });

        this.webSocketClient.on('message', this.handleIncomingMessage.bind(this));
        this.webSocketClient.on('notification', this.handleNotification.bind(this));

        this.webSocketClient.connect();
    }

    setupNotificationHandlers() {
        NotificationService.on('add', this.renderNotifications.bind(this));
        NotificationService.on('remove', this.renderNotifications.bind(this));
    }

    setupUserInterface() {
        this.createDashboardLayout();
        this.createNotificationPanel();
        this.createRequestManagementPanel();
    }

    setupEventListeners() {
        document.getElementById('logout-btn').addEventListener('click', this.logout.bind(this));
        document.getElementById('request-filter').addEventListener('change', this.filterRequests.bind(this));
    }

    createDashboardLayout() {
        const dashboardContainer = document.createElement('div');
        dashboardContainer.id = 'combined-dashboard';
        dashboardContainer.innerHTML = `
            <header>
                <h1>Hotel AI Management Dashboard</h1>
                <div id="connection-status" class="status-indicator"></div>
                <button id="logout-btn">Logout</button>
            </header>
            
            <div class="dashboard-grid">
                <div class="notifications-panel">
                    <h2>Notifications</h2>
                    <select id="request-filter">
                        <option value="all">All Requests</option>
                        <option value="room_service">Room Service</option>
                        <option value="housekeeping">Housekeeping</option>
                        <option value="maintenance">Maintenance</option>
                    </select>
                    <div id="notifications-container"></div>
                </div>
                
                <div class="request-management-panel">
                    <h2>Request Management</h2>
                    <div id="request-list"></div>
                </div>
            </div>
        `;
        document.body.appendChild(dashboardContainer);
    }

    createNotificationPanel() {
        const notificationsContainer = document.getElementById('notifications-container');
        const notifications = NotificationService.getAll();
        
        notificationsContainer.innerHTML = notifications.map(notification => `
            <div class="notification ${notification.priority}" data-id="${notification.id}">
                <span class="notification-type">${notification.type}</span>
                <span class="notification-message">${notification.message}</span>
                <span class="notification-time">${this.formatTime(notification.timestamp)}</span>
                <button class="dismiss-notification">✕</button>
            </div>
        `).join('');

        this.attachNotificationListeners();
    }

    createRequestManagementPanel() {
        const requestList = document.getElementById('request-list');
        // Populate with current requests from backend
        this.fetchCurrentRequests();
    }

    handleIncomingMessage(message) {
        if (message.type === 'request') {
            this.processRequest(message);
        }
    }

    handleNotification(notification) {
        NotificationService.add(notification);
    }

    processRequest(request) {
        // Logic to handle different types of requests
        switch (request.category) {
            case 'room_service':
                this.handleRoomServiceRequest(request);
                break;
            case 'housekeeping':
                this.handleHousekeepingRequest(request);
                break;
            case 'maintenance':
                this.handleMaintenanceRequest(request);
                break;
        }
    }

    handleRoomServiceRequest(request) {
        // Specific room service request handling
    }

    handleHousekeepingRequest(request) {
        // Specific housekeeping request handling
    }

    handleMaintenanceRequest(request) {
        // Specific maintenance request handling
    }

    renderNotifications() {
        this.createNotificationPanel();
    }

    filterRequests(event) {
        const filter = event.target.value;
        const requests = document.querySelectorAll('.request-item');
        
        requests.forEach(request => {
            const category = request.dataset.category;
            request.style.display = filter === 'all' || category === filter ? 'block' : 'none';
        });
    }

    updateConnectionStatus(isConnected) {
        const statusIndicator = document.getElementById('connection-status');
        statusIndicator.textContent = isConnected ? 'Connected' : 'Disconnected';
        statusIndicator.className = `status-indicator ${isConnected ? 'connected' : 'disconnected'}`;
    }

    fetchCurrentRequests() {
        // Fetch current requests from backend
        this.webSocketClient.emit('fetch_requests', {});
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleString();
    }

    attachNotificationListeners() {
        document.querySelectorAll('.dismiss-notification').forEach(button => {
            button.addEventListener('click', (event) => {
                const notificationId = event.target.closest('.notification').dataset.id;
                NotificationService.remove(notificationId);
            });
        });
    }

    logout() {
        // Implement logout logic
        this.webSocketClient.disconnect();
        // Redirect to login page or reset dashboard
    }

    getBackendUrl() {
        // Get backend URL from environment or configuration
        return process.env.BACKEND_URL || 'http://localhost:5000';
    }
}

export default new CombinedDashboard();