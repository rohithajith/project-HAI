import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Bookings API
export const bookingsApi = {
  getAll: () => api.get('/bookings'),
  getUpcoming: () => api.get('/bookings/upcoming'),
  getCurrent: () => api.get('/bookings/current'),
  getPast: () => api.get('/bookings/past'),
  getById: (id) => api.get(`/bookings/${id}`),
};

// Alerts API
export const alertsApi = {
  getAll: () => api.get('/alerts'),
  getCount: () => api.get('/alerts/count'),
  create: (alertData) => api.post('/alerts', alertData),
  resolve: (id) => api.put(`/alerts/${id}/resolve`),
  resetCount: () => api.post('/alerts/reset'),
};

// Notifications API
export const notificationsApi = {
  getAll: () => api.get('/notifications'),
  create: (notificationData) => api.post('/notifications', notificationData),
  getByRoom: (roomNumber) => api.get(`/notifications/room/${roomNumber}`),
  markAsRead: (id) => api.put(`/notifications/${id}/read`),
  sendLaundryAlert: (roomNumber) => api.post('/notifications/laundry', { room_number: roomNumber }),
};

// Chatbot API
export const chatbotApi = {
  sendMessage: (chatData) => api.post('/chatbot', chatData),
};

export default {
  bookings: bookingsApi,
  alerts: alertsApi,
  notifications: notificationsApi,
};