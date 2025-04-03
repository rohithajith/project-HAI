// Enhanced Notification Service for Hotel AI System

class NotificationService {
    constructor() {
        this.notifications = [];
        this.listeners = {};
        this.maxNotifications = 50;
    }

    // Add a new notification with strict validation
    add(notification) {
        if (!this.validateNotification(notification)) {
            console.warn('Invalid notification structure', notification);
            return false;
        }

        // Prevent duplicate notifications
        const exists = this.notifications.some(
            n => n.id === notification.id || 
                 (n.type === notification.type && 
                  n.room_number === notification.room_number)
        );

        if (!exists) {
            // Enrich notification with additional metadata
            const enrichedNotification = this.enrichNotification(notification);
            
            // Manage notification queue
            if (this.notifications.length >= this.maxNotifications) {
                this.notifications.shift(); // Remove oldest notification
            }

            this.notifications.push(enrichedNotification);
            this.triggerListeners('add', enrichedNotification);
            return true;
        }

        return false;
    }

    // Validate notification structure
    validateNotification(notification) {
        const requiredFields = ['type', 'agent', 'room_number'];
        const validTypes = [
            'housekeeping_request', 
            'order_started', 
            'maintenance_request', 
            'system_alert'
        ];
        const validAgents = [
            'room_service_agent', 
            'maintenance_agent', 
            'system_agent'
        ];

        return (
            requiredFields.every(field => 
                notification.hasOwnProperty(field) && 
                notification[field] !== null && 
                notification[field] !== undefined
            ) &&
            validTypes.includes(notification.type) &&
            validAgents.includes(notification.agent) &&
            /^\d{3}$/.test(notification.room_number)
        );
    }

    // Enrich notification with additional metadata
    enrichNotification(notification) {
        return {
            ...notification,
            id: notification.id || this.generateUniqueId(),
            timestamp: notification.timestamp || new Date().toISOString(),
            priority: this.determinePriority(notification),
            category: this.categorizeNotification(notification)
        };
    }

    // Generate a unique notification ID
    generateUniqueId() {
        return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Determine notification priority
    determinePriority(notification) {
        const priorityMap = {
            'housekeeping_request': 'medium',
            'order_started': 'high',
            'maintenance_request': 'high',
            'system_alert': 'critical'
        };
        return priorityMap[notification.type] || 'low';
    }

    // Categorize notification
    categorizeNotification(notification) {
        const categoryMap = {
            'housekeeping_request': 'housekeeping',
            'order_started': 'room_service',
            'maintenance_request': 'maintenance',
            'system_alert': 'admin'
        };
        return categoryMap[notification.type] || 'general';
    }

    // Remove a notification by ID
    remove(notificationId) {
        const index = this.notifications.findIndex(n => n.id === notificationId);
        if (index !== -1) {
            const removedNotification = this.notifications.splice(index, 1)[0];
            this.triggerListeners('remove', removedNotification);
            return true;
        }
        return false;
    }

    // Get notifications for a specific room
    getByRoom(roomNumber) {
        return this.notifications.filter(n => n.room_number === roomNumber);
    }

    // Get all notifications
    getAll() {
        return [...this.notifications];
    }

    // Filter notifications by criteria
    filter(criteria) {
        return this.notifications.filter(criteria);
    }

    // Clear all notifications
    clear() {
        const oldNotifications = [...this.notifications];
        this.notifications = [];
        this.triggerListeners('clear', oldNotifications);
    }

    // Add event listeners for notification changes
    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    // Trigger listeners for a specific event
    triggerListeners(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
}

export default new NotificationService();