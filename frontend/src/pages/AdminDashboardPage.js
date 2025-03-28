import React from 'react';

const AdminDashboardPage = () => {
    // Placeholder data - replace with actual data fetching later
    const bookings = {
        today: [{ id: 1, guest: 'Alice', room: 101 }, { id: 2, guest: 'Bob', room: 102 }],
        tomorrow: [{ id: 3, guest: 'Charlie', room: 201 }],
        yesterday: [{ id: 4, guest: 'David', room: 301 }],
    };
    const alerts = [{ id: 1, type: 'Emergency', room: 101, details: 'Fire alarm activated' }];
    const roomServiceItems = ['Towels', 'Tea', 'Pillows', 'Snack Basket']; // Example items

    const handleAddItemToRoomService = (item) => {
        // Placeholder function - implement logic to add item
        console.log(`Adding ${item} to Room Service options...`);
        alert(`${item} added to Room Service options (placeholder).`);
    };

    return (
        <div className="page-container">
            <h2>Admin Dashboard</h2>

            <section>
                <h3>Bookings</h3>
                <h4>Today</h4>
                <ul>{bookings.today.map(b => <li key={b.id}>Room {b.room} - {b.guest}</li>)}</ul>
                <h4>Tomorrow</h4>
                <ul>{bookings.tomorrow.map(b => <li key={b.id}>Room {b.room} - {b.guest}</li>)}</ul>
                <h4>Yesterday</h4>
                <ul>{bookings.yesterday.map(b => <li key={b.id}>Room {b.room} - {b.guest}</li>)}</ul>
            </section>

            <hr />

            <section>
                <h3>Emergency Alerts</h3>
                {alerts.length > 0 ? (
                    <ul>{alerts.map(a => <li key={a.id}>[{a.type}] Room {a.room}: {a.details}</li>)}</ul>
                ) : (
                    <p>No active alerts.</p>
                )}
            </section>

            <hr />

            <section>
                <h3>Manage Room Service Items</h3>
                {/* Simple form to add items - replace with better UI later */}
                <input type="text" id="newItemInput" placeholder="New item name" />
                <button onClick={() => {
                    const newItem = document.getElementById('newItemInput').value;
                    if (newItem) handleAddItemToRoomService(newItem);
                }}>
                    Add Item
                </button>
                <p>Current Items: {roomServiceItems.join(', ')}</p>
            </section>
        </div>
    );
};

export default AdminDashboardPage;