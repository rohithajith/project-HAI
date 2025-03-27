import React, { createContext, useState, useEffect } from 'react';
import socket from '../services/socket'; // Use default import for the initialized socket instance

export const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(socket.connected);

  useEffect(() => {
    function onConnect() {
      console.log('Socket connected:', socket.id);
      setIsConnected(true);
    }

    function onDisconnect() {
      console.log('Socket disconnected');
      setIsConnected(false);
    }

    // Register listeners
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);

    // Initial check in case already connected
    if (socket.connected) {
        setIsConnected(true);
    } else {
        // Attempt to connect if not already connected (optional, socket.js might handle this)
        // socket.connect();
    }


    // Cleanup listeners
    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []); // Run only once on mount

  // Provide the socket instance and connection status
  const contextValue = socket; // Directly provide the socket instance

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  );
};