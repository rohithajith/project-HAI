import React from "react";

const HeroBanner = () => {
  return (
    <div className="relative h-[90vh] bg-cover bg-center bg-[url('https://source.unsplash.com/1600x900/?luxury-hotel,resort')]">
      <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
        <div className="text-center text-white max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Welcome to Paradise Resort</h1>
          <p className="text-lg md:text-xl">Luxury redefined. Now with your personal AI assistant.</p>
        </div>
      </div>
    </div>
  );
};

export default HeroBanner;
