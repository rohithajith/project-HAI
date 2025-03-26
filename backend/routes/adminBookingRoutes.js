const express = require('express');
const router = express.Router();
const db = require('../config/database'); // Assuming dbAsync is exported
const { protect, restrictTo } = require('../middleware/authMiddleware'); // Correct import names

// Helper function to get date strings (YYYY-MM-DD)
const getDateString = (offsetDays = 0) => {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// GET /api/admin/bookings/filtered - Fetch bookings for previous, today, tomorrow
// Protected for admin/staff roles
router.get('/filtered', protect, restrictTo('admin', 'manager', 'staff'), async (req, res) => { // Use protect and restrictTo
  try {
    const today = getDateString(0);
    const tomorrow = getDateString(1);
    const previousDay = getDateString(-1);

    // Query explanation:
    // We need bookings that are *active* during these days.
    // - Active Today: check_in <= today AND check_out > today
    // - Active Tomorrow: check_in <= tomorrow AND check_out > tomorrow
    // - Active Previous Day: check_in <= previousDay AND check_out > previousDay
    // Note: This assumes check_out is the day *after* the last night stayed. Adjust if needed.
    // We also join with users and guest_profiles to get guest names.

    // Using guest_profiles for room number and users for names
    const sql = `
      SELECT
        bp.id,
        u.first_name || ' ' || u.last_name AS guestName,
        gp.room_number AS roomNumber,
        bp.check_in AS checkIn,
        bp.check_out AS checkOut
      FROM bookings bp -- Assuming a 'bookings' table exists
      JOIN users u ON bp.user_id = u.id
      JOIN guest_profiles gp ON u.id = gp.user_id
      WHERE
        -- Active Previous Day
        (bp.check_in <= ? AND bp.check_out > ?) OR
        -- Active Today
        (bp.check_in <= ? AND bp.check_out > ?) OR
        -- Active Tomorrow
        (bp.check_in <= ? AND bp.check_out > ?)
      ORDER BY bp.check_in, gp.room_number;
    `;

    const allRelevantBookings = await db.all(sql, [
      previousDay, previousDay,
      today, today,
      tomorrow, tomorrow
    ]);

    // Filter in application logic for clarity
    const filteredBookings = {
      previous: allRelevantBookings.filter(b => b.checkIn <= previousDay && b.checkOut > previousDay),
      today: allRelevantBookings.filter(b => b.checkIn <= today && b.checkOut > today),
      tomorrow: allRelevantBookings.filter(b => b.checkIn <= tomorrow && b.checkOut > tomorrow),
    };

    res.json(filteredBookings);

  } catch (error) {
    console.error('Error fetching filtered bookings:', error);
    res.status(500).json({ error: 'Failed to fetch bookings' });
  }
});

// Add other admin booking routes here if needed (e.g., create, update, delete)

module.exports = router;