"""
Pydantic schemas for request/response validation.
These ensure data integrity and provide automatic documentation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# Request Schemas (data coming IN to our API)
class BookingCreate(BaseModel):
    """Schema for creating a new booking"""
    class_id: int = Field(..., description="ID of the fitness class to book")
    client_name: str = Field(..., min_length=1, max_length=100, description="Client's full name")
    client_email: EmailStr = Field(..., description="Client's email address")
    
    model_config = ConfigDict(
        # This creates example data for API documentation
        json_schema_extra={
            "example": {
                "class_id": 1,
                "client_name": "John Doe",
                "client_email": "john.doe@example.com"
            }
        }
    )


# Response Schemas (data going OUT from our API)
class FitnessClassResponse(BaseModel):
    """Schema for fitness class response"""
    id: int
    name: str
    instructor: str
    datetime_ist: datetime = Field(..., description="Class date/time in IST")
    available_slots: int = Field(..., description="Number of available slots")
    total_slots: int
    
    model_config = ConfigDict(
        # Allow ORM models to be converted to Pydantic
        from_attributes=True
    )


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: int
    class_id: int
    client_name: str
    client_email: str
    booked_at_ist: datetime = Field(..., description="Booking timestamp in IST")
    
    # Include class details in response
    fitness_class: FitnessClassResponse
    
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Generic message response for status messages"""
    message: str
    details: Optional[dict] = None


# List response schemas
class ClassListResponse(BaseModel):
    """Response containing list of classes"""
    total: int
    classes: List[FitnessClassResponse]


class BookingListResponse(BaseModel):
    """Response containing list of bookings"""
    total: int
    bookings: List[BookingResponse]