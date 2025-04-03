import NotificationService from '../src/notification_service';

describe('NotificationService', () => {
    let notificationService;

    beforeEach(() => {
        // Reset the singleton instance before each test
        notificationService = new NotificationService();
    });

    test('add method adds unique notifications', () => {
        const notification1 = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification',
            timestamp: new Date().toISOString()
        };

        const notification2 = { 
            id: '2', 
            type: 'housekeeping', 
            message: 'Another notification',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification1);
        notificationService.add(notification2);

        expect(notificationService.getAll()).toHaveLength(2);
    });

    test('add method prevents duplicate notifications', () => {
        const notification = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification);
        notificationService.add(notification);

        expect(notificationService.getAll()).toHaveLength(1);
    });

    test('remove method removes specific notification', () => {
        const notification1 = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification 1',
            timestamp: new Date().toISOString()
        };

        const notification2 = { 
            id: '2', 
            type: 'housekeeping', 
            message: 'Test notification 2',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification1);
        notificationService.add(notification2);

        notificationService.remove('1');

        expect(notificationService.getAll()).toHaveLength(1);
        expect(notificationService.getAll()[0].id).toBe('2');
    });

    test('clear method removes all notifications', () => {
        const notification1 = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification 1',
            timestamp: new Date().toISOString()
        };

        const notification2 = { 
            id: '2', 
            type: 'housekeeping', 
            message: 'Test notification 2',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification1);
        notificationService.add(notification2);

        notificationService.clear();

        expect(notificationService.getAll()).toHaveLength(0);
    });

    test('filter method returns notifications based on criteria', () => {
        const notification1 = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification 1',
            timestamp: new Date().toISOString()
        };

        const notification2 = { 
            id: '2', 
            type: 'housekeeping', 
            message: 'Test notification 2',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification1);
        notificationService.add(notification2);

        const roomServiceNotifications = notificationService.filter(
            n => n.type === 'room_service'
        );

        expect(roomServiceNotifications).toHaveLength(1);
        expect(roomServiceNotifications[0].id).toBe('1');
    });

    test('categorize method correctly categorizes notifications', () => {
        const roomServiceNotification = { 
            id: '1', 
            type: 'order_started', 
            message: 'Room service order started'
        };

        const housekeepingNotification = { 
            id: '2', 
            type: 'housekeeping_request', 
            message: 'Room cleaning requested'
        };

        const maintenanceNotification = { 
            id: '3', 
            type: 'maintenance_request', 
            message: 'Repair needed'
        };

        const adminNotification = { 
            id: '4', 
            type: 'system_alert', 
            message: 'System update required'
        };

        expect(notificationService.categorize(roomServiceNotification)).toBe('room_service');
        expect(notificationService.categorize(housekeepingNotification)).toBe('housekeeping');
        expect(notificationService.categorize(maintenanceNotification)).toBe('maintenance');
        expect(notificationService.categorize(adminNotification)).toBe('admin');
    });

    test('prioritize method correctly prioritizes notifications', () => {
        const highPriorityNotification = { 
            id: '1', 
            type: 'maintenance_request', 
            message: 'Urgent repair needed'
        };

        const mediumPriorityNotification = { 
            id: '2', 
            type: 'order_started', 
            message: 'Room service order in progress'
        };

        const lowPriorityNotification = { 
            id: '3', 
            type: 'booking_update', 
            message: 'Booking details updated'
        };

        expect(notificationService.prioritize(highPriorityNotification)).toBe('high');
        expect(notificationService.prioritize(mediumPriorityNotification)).toBe('medium');
        expect(notificationService.prioritize(lowPriorityNotification)).toBe('low');
    });

    test('on method registers event listeners', () => {
        const mockAddListener = jest.fn();
        const mockRemoveListener = jest.fn();

        notificationService.on('add', mockAddListener);
        notificationService.on('remove', mockRemoveListener);

        const notification = { 
            id: '1', 
            type: 'room_service', 
            message: 'Test notification',
            timestamp: new Date().toISOString()
        };

        notificationService.add(notification);
        notificationService.remove('1');

        expect(mockAddListener).toHaveBeenCalledWith(notification);
        expect(mockRemoveListener).toHaveBeenCalledWith(notification);
    });
});