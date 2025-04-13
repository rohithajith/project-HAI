import React from "react";

const HeroSection = () => {
  return (
    <div className="bg-cover bg-center h-[90vh] text-white flex items-center justify-center bg-[url('https://images.unsplash.com/photo-1600488991382-7c03d7e8e165')]">
      <div className="text-center bg-black/50 p-8 rounded-lg">
        <h1 className="text-4xl font-bold mb-4">Welcome to the Resort</h1>
        <p className="text-lg">Your luxury stay with smart AI-powered assistance</p>
      </div>
    </div>
  );
};

export default HeroSection;
