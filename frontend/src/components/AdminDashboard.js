import React, { useState, useEffect } from 'react';
import WebSocketService from '../services/websocket-service';

function AdminDashboard() {
    const [agentInteractions, setAgentInteractions] = useState([]);
    const [systemNotifications, setSystemNotifications] = useState([]);

    useEffect(() => {
        // Initialize WebSocket connection
        WebSocketService.connect();

        // Add listener for admin dashboard updates
        const handleAgentUpdate = (updateData) => {
            console.log('Admin Dashboard Update:', updateData);

            // Log all agent interactions
            setAgentInteractions(prev => [
                ...prev,
                {
                    timestamp: new Date().toLocaleString(),
                    agent: updateData.details?.agent || 'Unknown Agent',
                    message: updateData.message,
                    details: updateData.details
                }
            ]);

            // Handle specific system notifications
            if (updateData.action === 'system_alert') {
                setSystemNotifications(prev => [
                    ...prev,
                    {
                        timestamp: new Date().toLocaleString(),
                        message: updateData.message,
                        severity: updateData.details?.severity || 'info'
                    }
                ]);
            }
        };

        WebSocketService.addListener('admin_dashboard', handleAgentUpdate);

        // Cleanup on component unmount
        return () => {
            WebSocketService.disconnect();
        };
    }, []);

    return (
        <div className="admin-dashboard">
            <h2>Admin Dashboard</h2>

            <section className="agent-interactions">
                <h3>Agent Interactions</h3>
                {agentInteractions.map((interaction, index) => (
                    <div key={index} className="interaction">
                        <strong>{interaction.agent}</strong>: 
                        {interaction.message} 
                        <small>{interaction.timestamp}</small>
                        <details>
                            <summary>Details</summary>
                            <pre>{JSON.stringify(interaction.details, null, 2)}</pre>
                        </details>
                    </div>
                ))}
            </section>

            <section className="system-notifications">
                <h3>System Notifications</h3>
                {systemNotifications.map((notification, index) => (
                    <div 
                        key={index} 
                        className={`notification notification-${notification.severity}`}
                    >
                        {notification.message} 
                        <small>{notification.timestamp}</small>
                    </div>
                ))}
            </section>
        </div>
    );
}

export default AdminDashboard;