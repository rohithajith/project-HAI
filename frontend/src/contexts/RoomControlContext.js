import React, { createContext, useState, useEffect, useContext } from 'react';

const RoomControlContext = createContext();

export const RoomControlProvider = ({ children }) => {
  // Initial state with default values
  const [temperature, setTemperature] = useState(23);
  const [brightness, setBrightness] = useState(70);
  const [colorTemp, setColorTemp] = useState(50); // 0-100 (warm to cool)
  const [activePreset, setActivePreset] = useState(null);
  
  // Load saved settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('roomControlSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setTemperature(parsed.temperature || 23);
        setBrightness(parsed.brightness || 70);
        setColorTemp(parsed.colorTemp || 50);
        setActivePreset(parsed.activePreset || null);
      } catch (error) {
        console.error('Error parsing saved room settings:', error);
      }
    }
  }, []);
  
  // Save settings to localStorage when they change
  useEffect(() => {
    localStorage.setItem('roomControlSettings', JSON.stringify({
      temperature,
      brightness,
      colorTemp,
      activePreset
    }));
  }, [temperature, brightness, colorTemp, activePreset]);
  
  // Preset definitions
  const presets = {
    sleep: {
      name: 'Sleep',
      icon: '😴',
      temperature: 20,
      brightness: 10,
      colorTemp: 20 // Warm
    },
    reading: {
      name: 'Reading',
      icon: '📖',
      temperature: 23,
      brightness: 60,
      colorTemp: 30 // Warm
    },
    eco: {
      name: 'Eco',
      icon: '🌱',
      temperature: 25, // Summer setting (would be 19 in winter)
      brightness: 30,
      colorTemp: 70 // Cool
    },
    custom: {
      name: 'Custom',
      icon: '🏠',
      // Uses current settings
      temperature,
      brightness,
      colorTemp
    }
  };
  
  // Apply a preset
  const applyPreset = (presetName) => {
    if (!presets[presetName]) return;
    
    const preset = presets[presetName];
    setTemperature(preset.temperature);
    setBrightness(preset.brightness);
    setColorTemp(preset.colorTemp);
    setActivePreset(presetName);
  };
  
  // Save current settings as custom preset
  const saveCustomPreset = () => {
    presets.custom = {
      ...presets.custom,
      temperature,
      brightness,
      colorTemp
    };
    setActivePreset('custom');
  };
  
  return (
    <RoomControlContext.Provider
      value={{
        temperature,
        setTemperature,
        brightness,
        setBrightness,
        colorTemp,
        setColorTemp,
        activePreset,
        setActivePreset,
        presets,
        applyPreset,
        saveCustomPreset
      }}
    >
      {children}
    </RoomControlContext.Provider>
  );
};

export const useRoomControl = () => {
  const context = useContext(RoomControlContext);
  if (!context) {
    throw new Error('useRoomControl must be used within a RoomControlProvider');
  }
  return context;
};

export default RoomControlContext;