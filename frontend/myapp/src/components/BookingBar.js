import React from "react";

const BookingBar = () => {
  return (
    <div className="flex flex-wrap justify-center items-center gap-3 bg-white shadow-lg p-4 -mt-10 mx-auto w-[90%] rounded-xl relative z-10">
      <select className="p-2 border rounded w-full md:w-1/5">
        <option>Select a Hotel</option>
        <option>Paradise Goa</option>
        <option>Paradise Jaipur</option>
      </select>
      <input type="text" className="p-2 border rounded w-full md:w-1/5" placeholder="Check-in - Check-out" />
      <input type="text" className="p-2 border rounded w-full md:w-1/5" placeholder="1 Room, 2 Adults" />
      <input type="text" className="p-2 border rounded w-full md:w-1/5" placeholder="Promo Code" />
      <button className="bg-orange-600 text-white px-4 py-2 rounded md:w-1/5 w-full hover:bg-orange-700">BOOK</button>
    </div>
  );
};

export default BookingBar;
