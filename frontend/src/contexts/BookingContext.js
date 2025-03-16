import React, { createContext, useState, useEffect, useContext } from 'react';
import { bookingsApi } from '../services/api';
import socketService from '../services/socket';

// Create context
const BookingContext = createContext();

// Custom hook to use the booking context
export const useBookings = () => useContext(BookingContext);

// Provider component
export const BookingProvider = ({ children }) => {
  const [allBookings, setAllBookings] = useState([]);
  const [upcomingBookings, setUpcomingBookings] = useState([]);
  const [currentBookings, setCurrentBookings] = useState([]);
  const [pastBookings, setPastBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all bookings
  const fetchAllBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingsApi.getAll();
      setAllBookings(response.data.data.bookings);
      setError(null);
    } catch (err) {
      setError('Failed to fetch bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch upcoming bookings
  const fetchUpcomingBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingsApi.getUpcoming();
      setUpcomingBookings(response.data.data.bookings);
      setError(null);
    } catch (err) {
      setError('Failed to fetch upcoming bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch current bookings
  const fetchCurrentBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingsApi.getCurrent();
      setCurrentBookings(response.data.data.bookings);
      setError(null);
    } catch (err) {
      setError('Failed to fetch current bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch past bookings
  const fetchPastBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingsApi.getPast();
      setPastBookings(response.data.data.bookings);
      setError(null);
    } catch (err) {
      setError('Failed to fetch past bookings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch booking by ID
  const fetchBookingById = async (id) => {
    try {
      const response = await bookingsApi.getById(id);
      return response.data.data.booking;
    } catch (err) {
      setError(`Failed to fetch booking with ID ${id}`);
      console.error(err);
      throw err;
    }
  };

  // Fetch all categories of bookings
  const fetchAllCategories = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchUpcomingBookings(),
        fetchCurrentBookings(),
        fetchPastBookings()
      ]);
      setError(null);
    } catch (err) {
      setError('Failed to fetch booking categories');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Initialize data and WebSocket listeners
  useEffect(() => {
    // Fetch initial data
    fetchAllCategories();

    // Connect to WebSocket
    socketService.connect();

    // Listen for new bookings
    socketService.on('new_booking', (booking) => {
      // Update appropriate category based on booking dates
      const now = new Date();
      const checkIn = new Date(booking.check_in);
      const checkOut = new Date(booking.check_out);

      if (checkIn > now) {
        setUpcomingBookings(prev => [booking, ...prev]);
      } else if (checkIn <= now && checkOut >= now) {
        setCurrentBookings(prev => [booking, ...prev]);
      } else {
        setPastBookings(prev => [booking, ...prev]);
      }

      // Also update all bookings
      setAllBookings(prev => [booking, ...prev]);
    });

    // Listen for booking updates
    socketService.on('booking_updated', (updatedBooking) => {
      // Update in all categories
      const updateBookingInList = (list) => 
        list.map(booking => booking.id === updatedBooking.id ? updatedBooking : booking);

      setAllBookings(updateBookingInList);
      setUpcomingBookings(updateBookingInList);
      setCurrentBookings(updateBookingInList);
      setPastBookings(updateBookingInList);
    });

    // Cleanup
    return () => {
      socketService.off('new_booking');
      socketService.off('booking_updated');
    };
  }, []);

  // Context value
  const value = {
    allBookings,
    upcomingBookings,
    currentBookings,
    pastBookings,
    loading,
    error,
    fetchAllBookings,
    fetchUpcomingBookings,
    fetchCurrentBookings,
    fetchPastBookings,
    fetchBookingById,
    fetchAllCategories
  };

  return (
    <BookingContext.Provider value={value}>
      {children}
    </BookingContext.Provider>
  );
};

export default BookingContext;