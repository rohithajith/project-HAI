import React from 'react';
import { AlertProvider } from './AlertContext';
import { BookingProvider } from './BookingContext';
import { NotificationProvider } from './NotificationContext';

// Combined provider component
export const AppProvider = ({ children }) => {
  return (
    <AlertProvider>
      <BookingProvider>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </BookingProvider>
    </AlertProvider>
  );
};

export default AppProvider;