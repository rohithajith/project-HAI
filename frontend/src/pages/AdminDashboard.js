import React from 'react';
import AdminBookings from '../components/admin/AdminBookings'; // Import the new component
// Import necessary components for tabs later
// import Bookings from './Bookings'; // Assuming Bookings component exists or will be created
// import Services from '../components/admin/Services'; // Example path
// import Settings from '../components/admin/Settings'; // Example path
// import Chatbot from '../components/common/Chatbot'; // Example path

const AdminDashboard = () => {
  // State to manage active tab, e.g., 'bookings', 'services', 'settings', 'chatbot'
  const [activeTab, setActiveTab] = React.useState('bookings');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'bookings':
        return <AdminBookings />; // Use the imported component
      case 'services':
        // return <Services />;
        return <div>Services Content (To be implemented)</div>;
      case 'settings':
        // return <Settings />;
        return <div>Settings Content (To be implemented)</div>;
      case 'chatbot':
        // return <Chatbot />;
        return <div>Chatbot Interface (To be implemented)</div>;
      default:
        return <div>Bookings Content (To be implemented)</div>;
    }
  };

  return (
    <div>
      <h1>Admin Dashboard</h1>
      <nav>
        {/* Basic tab navigation */}
        <button onClick={() => setActiveTab('bookings')} disabled={activeTab === 'bookings'}>Bookings</button>
        <button onClick={() => setActiveTab('services')} disabled={activeTab === 'services'}>Services</button>
        <button onClick={() => setActiveTab('settings')} disabled={activeTab === 'settings'}>Settings</button>
        <button onClick={() => setActiveTab('chatbot')} disabled={activeTab === 'chatbot'}>Chatbot</button>
        {/* Add SOS Alert indicator if needed based on sketch */}
      </nav>
      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default AdminDashboard;