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
        const response = await bookingsApi.create({
          message: "Get room data",
          queryType: "room_data"
        });
        setRoomData(response.data);
      } catch (error) {
        console.error('Error fetching room data:', error);
      }
    };

    fetchRoomData();
  }, []);

  const handleTempChange = async (newTemp) => {
    try {
      await bookingsApi.create({
        request: `Set temperature to ${newTemp}°C`
      });
      setRoomData(prev => ({ ...prev, temperature: newTemp }));
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