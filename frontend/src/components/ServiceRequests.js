import React from 'react';
import './ServiceRequests.css';

const ServiceRequests = ({ requests }) => {
  if (requests.length === 0) return null;

  return (
    <div className="service-requests">
      <h3>Your Active Requests</h3>
      <ul>
        {requests.map((request, index) => (
          <li key={index} className="request-item">
            <div className="request-type">{request.type}</div>
            <div className="request-message">{request.message}</div>
            <div className="request-status">Processing...</div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ServiceRequests;