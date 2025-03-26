import React, { useState } from 'react';
import './ThermostatControl.css';

const ThermostatControl = ({ currentTemp, onTempChange }) => {
  const [temperature, setTemperature] = useState(currentTemp);

  const handleChange = (e) => {
    const newTemp = parseInt(e.target.value);
    setTemperature(newTemp);
    onTempChange(newTemp);
  };

  return (
    <div className="thermostat-control">
      <h3>Room Temperature Control</h3>
      <div className="temp-display">
        {temperature}°C
      </div>
      <input 
        type="range"
        min="16"
        max="30"
        value={temperature}
        onChange={handleChange}
        className="temp-slider"
      />
      <div className="temp-labels">
        <span>16°C</span>
        <span>30°C</span>
      </div>
    </div>
  );
};

export default ThermostatControl;