import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { bookingsApi } from '../services/api';
import ChatbotInterface from './ChatbotInterface';
import ThermostatControl from './ThermostatControl';
import ServiceRequests from './ServiceRequests';

const GuestPortal = () => {
  const { currentUser } = useAuth();
  const [roomData, setRoomData] = useState({
    temperature: 22,
    services: []
  });
  const [showChatbot, setShowChatbot] = useState(false);

  useEffect(() => {
    // Fetch initial room data
    const fetchRoomData = async () => {
      try {
        // Use getCurrent() instead of non-existent create()
        const response = await bookingsApi.getCurrent();
        // Merge response data with existing state, ensuring services is always an array
        setRoomData(prevData => ({
          ...prevData, // Keep existing state
          ...(response.data || {}), // Merge response data (if any)
          services: response.data?.services || prevData.services || [] // Ensure services is an array
        }));
      } catch (error) {
        console.error('Error fetching room data:', error);
        // Optionally set default state on error
        // setRoomData(prevData => ({ ...prevData, services: prevData.services || [] }));
      }
    };

    fetchRoomData();
  }, []);

  const handleTempChange = async (newTemp) => {
    try {
      // TODO: Implement backend endpoint for setting temperature
      // await bookingsApi.create({ // Commented out - 'create' doesn't exist
      //   request: `Set temperature to ${newTemp}°C`
      // });
      setRoomData(prev => ({ ...prev, temperature: newTemp })); // Update local state only for now
    } catch (error) {
      console.error('Error setting temperature:', error);
    }
  };

  return (
    <div className="guest-portal">
      <h2>Welcome, {currentUser?.firstName || 'Guest'}</h2>
      
      <div className="room-controls">
        <ThermostatControl 
          currentTemp={roomData.temperature} 
          onTempChange={handleTempChange}
        />
        
        <button 
          className="chatbot-button"
          onClick={() => setShowChatbot(!showChatbot)}
        >
          {showChatbot ? 'Hide Chatbot' : 'Open AI Concierge'}
        </button>
      </div>

      {showChatbot && (
        <ChatbotInterface 
          roomNumber={currentUser?.roomNumber}
          onServiceRequest={(service) => {
            setRoomData(prev => ({
              ...prev,
              services: [...prev.services, service]
            }));
          }}
        />
      )}

      <ServiceRequests requests={roomData.services} />
    </div>
  );
};

export default GuestPortal;