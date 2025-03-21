"""
Specialized schemas for specific agents in the Hotel AI Assistant.

This module defines the input/output schemas for each specialized agent,
extending the base schemas with agent-specific fields.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from .base import AgentInput, AgentOutput, AgentMessage


# Check-in Agent Schemas

class CheckInInput(AgentInput):
    """Input schema for the Check-in Agent."""
    
    booking_id: Optional[str] = Field(None, description="Booking ID for the check-in")
    guest_name: Optional[str] = Field(None, description="Name of the guest checking in")
    id_verification: Optional[bool] = Field(None, description="Whether ID has been verified")
    payment_verification: Optional[bool] = Field(None, description="Whether payment has been verified")


class CheckInOutput(AgentOutput):
    """Output schema for the Check-in Agent."""
    
    booking_details: Optional[Dict[str, Any]] = Field(None, description="Details of the booking")
    check_in_status: Optional[str] = Field(None, description="Status of the check-in process")
    room_number: Optional[str] = Field(None, description="Assigned room number")
    key_issued: Optional[bool] = Field(None, description="Whether a key has been issued")


# Room Service Agent Schemas

class RoomServiceInput(AgentInput):
    """Input schema for the Room Service Agent."""
    
    room_number: Optional[str] = Field(None, description="Room number for the service request")
    request_type: Optional[str] = Field(None, description="Type of room service request (e.g., towels, pillows)")
    quantity: Optional[int] = Field(None, description="Quantity of items requested")
    special_instructions: Optional[str] = Field(None, description="Special instructions for the request")


class RoomServiceOutput(AgentOutput):
    """Output schema for the Room Service Agent."""
    
    request_id: Optional[str] = Field(None, description="ID of the service request")
    estimated_delivery_time: Optional[datetime] = Field(None, description="Estimated time of delivery")
    status: str = Field(..., description="Status of the service request")
    assigned_staff: Optional[str] = Field(None, description="Staff member assigned to the request")


# Wellness Agent Schemas

class WellnessInput(AgentInput):
    """Input schema for the Wellness Agent."""
    
    session_type: Optional[str] = Field(None, description="Type of wellness session (e.g., meditation, breathing)")
    duration: Optional[int] = Field(None, description="Duration of the session in minutes")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences for the session")


class WellnessOutput(AgentOutput):
    """Output schema for the Wellness Agent."""
    
    session_id: Optional[str] = Field(None, description="ID of the wellness session")
    session_content: Optional[str] = Field(None, description="Content of the wellness session")
    follow_up_recommendations: Optional[List[str]] = Field(None, description="Recommendations for follow-up sessions")


# Entertainment Agent Schemas

class EntertainmentInput(AgentInput):
    """Input schema for the Entertainment Agent."""
    
    content_type: Optional[str] = Field(None, description="Type of entertainment content (e.g., sleep story, music)")
    genre: Optional[str] = Field(None, description="Genre preference")
    duration: Optional[int] = Field(None, description="Preferred duration in minutes")


class EntertainmentOutput(AgentOutput):
    """Output schema for the Entertainment Agent."""
    
    content_id: Optional[str] = Field(None, description="ID of the entertainment content")
    content_title: Optional[str] = Field(None, description="Title of the entertainment content")
    content_description: Optional[str] = Field(None, description="Description of the entertainment content")
    content_url: Optional[str] = Field(None, description="URL to access the entertainment content")


# Cab Booking Agent Schemas

class CabBookingInput(AgentInput):
    """Input schema for the Cab Booking Agent."""
    
    pickup_location: Optional[str] = Field(None, description="Pickup location")
    destination: Optional[str] = Field(None, description="Destination")
    pickup_time: Optional[datetime] = Field(None, description="Requested pickup time")
    passengers: Optional[int] = Field(None, description="Number of passengers")
    cab_type: Optional[str] = Field(None, description="Type of cab (e.g., standard, premium)")


class CabBookingOutput(AgentOutput):
    """Output schema for the Cab Booking Agent."""
    
    booking_id: Optional[str] = Field(None, description="ID of the cab booking")
    driver_details: Optional[Dict[str, Any]] = Field(None, description="Details of the assigned driver")
    vehicle_details: Optional[Dict[str, Any]] = Field(None, description="Details of the assigned vehicle")
    estimated_arrival: Optional[datetime] = Field(None, description="Estimated arrival time of the cab")
    fare_estimate: Optional[float] = Field(None, description="Estimated fare for the trip")


# Extend Stay Agent Schemas

class ExtendStayInput(AgentInput):
    """Input schema for the Extend Stay Agent."""
    
    booking_id: Optional[str] = Field(None, description="Booking ID")
    room_number: Optional[str] = Field(None, description="Room number")
    additional_nights: Optional[int] = Field(None, description="Number of additional nights")
    reason: Optional[str] = Field(None, description="Reason for extending stay")


class ExtendStayOutput(AgentOutput):
    """Output schema for the Extend Stay Agent."""
    
    request_id: Optional[str] = Field(None, description="ID of the extension request")
    availability: Optional[bool] = Field(None, description="Whether the room is available for the extended period")
    updated_checkout_date: Optional[datetime] = Field(None, description="Updated checkout date if approved")
    additional_charges: Optional[float] = Field(None, description="Additional charges for the extended stay")
    approval_status: Optional[str] = Field(None, description="Status of the approval (pending, approved, rejected)")