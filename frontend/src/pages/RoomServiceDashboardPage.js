import React, { useState, useEffect } from 'react';

const RoomServiceDashboardPage = () => {
    // Placeholder state for room service requests
    // In a real app, this would likely come from WebSocket or API calls
    const [requests, setRequests] = useState([
        { id: 1, room: 102, item: 'Towels', status: 'Pending' },
        { id: 2, room: 205, item: 'Tea', status: 'Pending' },
        { id: 3, room: 102, item: 'Pillows', status: 'Delivered' },
        { id: 4, room: 310, item: 'Snack Basket', status: 'Pending' },
    ]);

    // Placeholder effect for simulating updates (e.g., via WebSocket)
    useEffect(() => {
        // Simulate a new request appearing after 10 seconds
        const timer = setTimeout(() => {
            setRequests(prevRequests => [
                ...prevRequests,
                { id: Date.now(), room: 401, item: 'Water Bottle', status: 'Pending' }
            ]);
        }, 10000);

        return () => clearTimeout(timer); // Cleanup timer on unmount
    }, []);

    const handleUpdateRequestStatus = (requestId, newStatus) => {
        setRequests(prevRequests =>
            prevRequests.map(req =>
                req.id === requestId ? { ...req, status: newStatus } : req
            )
        );
        console.log(`Updating request ${requestId} to ${newStatus} (placeholder).`);
        // In real app, send update to backend here
    };


    return (
        <div className="page-container">
            <h2>Room Service Dashboard</h2>
            <p>Displaying guest requests for items like towels, tea, pillows, food, etc.</p>

            <table>
                <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Room</th>
                        <th>Item</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {requests.map(req => (
                        <tr key={req.id}>
                            <td>{req.id}</td>
                            <td>{req.room}</td>
                            <td>{req.item}</td>
                            <td>{req.status}</td>
                            <td>
                                {req.status === 'Pending' && (
                                    <>
                                        <button onClick={() => handleUpdateRequestStatus(req.id, 'In Progress')}>Start</button>
                                        <button onClick={() => handleUpdateRequestStatus(req.id, 'Delivered')}>Deliver</button>
                                    </>
                                )}
                                {req.status === 'In Progress' && (
                                    <button onClick={() => handleUpdateRequestStatus(req.id, 'Delivered')}>Deliver</button>
                                )}
                                {req.status === 'Delivered' && (
                                    <span>Completed</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default RoomServiceDashboardPage;