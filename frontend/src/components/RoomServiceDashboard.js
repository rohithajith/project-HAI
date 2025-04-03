import React, { useState, useEffect } from 'react';
import WebSocketService from '../services/websocket-service';

function RoomServiceDashboard() {
    const [notifications, setNotifications] = useState([]);
    const [currentOrders, setCurrentOrders] = useState([]);
    const [housekeepingRequests, setHousekeepingRequests] = useState([]);

    useEffect(() => {
        // Initialize WebSocket connection
        WebSocketService.connect();

        // Add listener for room service dashboard updates
        const handleAgentUpdate = (updateData) => {
            console.log('Dashboard Update:', updateData);

            switch(updateData.action) {
                case 'show_notification':
                    setNotifications(prev => [
                        ...prev, 
                        {
                            message: updateData.message,
                            timestamp: new Date().toLocaleString()
                        }
                    ]);
                    break;

                case 'add_order':
                    setCurrentOrders(prev => [
                        ...prev,
                        {
                            id: `order-${prev.length + 1}`,
                            details: updateData.details,
                            timestamp: new Date().toLocaleString()
                        }
                    ]);
                    break;

                case 'highlight_menu':
                    // Trigger menu highlight animation or modal
                    console.log('Menu should be highlighted');
                    break;

                default:
                    console.warn('Unhandled dashboard action:', updateData.action);
            }
        };

        WebSocketService.addListener('room_service_dashboard', handleAgentUpdate);

        // Cleanup on component unmount
        return () => {
            WebSocketService.disconnect();
        };
    }, []);

    return (
        <div className="room-service-dashboard">
            <h2>Room Service Dashboard</h2>

            <section className="notifications">
                <h3>Notifications</h3>
                {notifications.map((notification, index) => (
                    <div key={index} className="notification">
                        {notification.message} - {notification.timestamp}
                    </div>
                ))}
            </section>

            <section className="current-orders">
                <h3>Current Orders</h3>
                {currentOrders.map((order) => (
                    <div key={order.id} className="order">
                        Order Details: {JSON.stringify(order.details)}
                        Timestamp: {order.timestamp}
                    </div>
                ))}
            </section>

            <section className="housekeeping-requests">
                <h3>Housekeeping Requests</h3>
                {housekeepingRequests.map((request, index) => (
                    <div key={index} className="request">
                        {request.details} - {request.timestamp}
                    </div>
                ))}
            </section>
        </div>
    );
}

export default RoomServiceDashboard;