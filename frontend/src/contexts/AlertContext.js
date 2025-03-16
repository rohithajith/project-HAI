import React, { createContext, useState, useEffect, useContext } from 'react';
import { alertsApi } from '../services/api';
import socketService from '../services/socket';

// Create context
const AlertContext = createContext();

// Custom hook to use the alert context
export const useAlerts = () => useContext(AlertContext);

// Provider component
export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);
  const [alertCount, setAlertCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all alerts
  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertsApi.getAll();
      setAlerts(response.data.data.alerts);
      setError(null);
    } catch (err) {
      setError('Failed to fetch alerts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch alert count
  const fetchAlertCount = async () => {
    try {
      const response = await alertsApi.getCount();
      setAlertCount(response.data.data.count);
    } catch (err) {
      console.error('Failed to fetch alert count:', err);
    }
  };

  // Create a new alert
  const createAlert = async (alertData) => {
    try {
      const response = await alertsApi.create(alertData);
      setAlerts([response.data.data.alert, ...alerts]);
      return response.data.data.alert;
    } catch (err) {
      setError('Failed to create alert');
      console.error(err);
      throw err;
    }
  };

  // Resolve an alert
  const resolveAlert = async (id) => {
    try {
      const response = await alertsApi.resolve(id);
      setAlerts(alerts.map(alert => 
        alert.id === id ? response.data.data.alert : alert
      ));
      return response.data.data.alert;
    } catch (err) {
      setError('Failed to resolve alert');
      console.error(err);
      throw err;
    }
  };

  // Reset alert count
  const resetAlertCount = async () => {
    try {
      const response = await alertsApi.resetCount();
      setAlertCount(response.data.data.count);
      return response.data.data.count;
    } catch (err) {
      setError('Failed to reset alert count');
      console.error(err);
      throw err;
    }
  };

  // Trigger an alert via WebSocket
  const triggerAlert = () => {
    socketService.triggerAlert();
  };

  // Initialize data and WebSocket listeners
  useEffect(() => {
    // Fetch initial data
    fetchAlerts();
    fetchAlertCount();

    // Connect to WebSocket
    socketService.connect();

    // Listen for alert count updates
    socketService.on('alert_count_updated', (count) => {
      setAlertCount(count);
    });

    // Listen for new alerts
    socketService.on('new_alert', (alert) => {
      setAlerts(prevAlerts => [alert, ...prevAlerts]);
    });

    // Listen for resolved alerts
    socketService.on('alert_resolved', (alert) => {
      setAlerts(prevAlerts => 
        prevAlerts.map(a => a.id === alert.id ? alert : a)
      );
    });

    // Cleanup
    return () => {
      socketService.off('alert_count_updated');
      socketService.off('new_alert');
      socketService.off('alert_resolved');
    };
  }, []);

  // Context value
  const value = {
    alerts,
    alertCount,
    loading,
    error,
    fetchAlerts,
    fetchAlertCount,
    createAlert,
    resolveAlert,
    resetAlertCount,
    triggerAlert
  };

  return (
    <AlertContext.Provider value={value}>
      {children}
    </AlertContext.Provider>
  );
};

export default AlertContext;