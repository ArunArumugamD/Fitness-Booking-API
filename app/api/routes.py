"""
API route definitions with comprehensive error handling.
FastAPI uses Python type hints to validate requests and generate documentation.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from .. import crud, schemas, models
from .dependencies import get_pagination_params, validate_email_query


# Create API router with prefix and tags for organization
router = APIRouter(
    prefix="/api/v1",
    tags=["fitness-classes"],
    responses={404: {"description": "Not found"}},
)


# 1. GET /classes - Get all upcoming fitness classes
@router.get(
    "/classes",
    response_model=schemas.ClassListResponse,
    summary="Get upcoming fitness classes",
    description="Returns a list of all upcoming fitness classes with available slots"
)
async def get_classes(
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """
    Retrieve all upcoming fitness classes.
    
    - **skip**: Number of classes to skip (for pagination)
    - **limit**: Maximum number of classes to return (max 100)
    
    Returns classes sorted by date/time in ascending order.
    """
    try:
        # Get upcoming classes from database
        classes = crud.get_upcoming_classes(
            db, 
            skip=pagination["skip"], 
            limit=pagination["limit"]
        )
        
        # Return structured response
        return schemas.ClassListResponse(
            total=len(classes),
            classes=classes
        )
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error fetching classes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching classes"
        )


# 2. POST /book - Create a new booking
@router.post(
    "/book",
    response_model=schemas.BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Book a fitness class",
    description="Create a new booking for a fitness class if slots are available"
)
async def create_booking(
    booking_data: schemas.BookingCreate,
    db: Session = Depends(get_db)
):
    """
    Book a spot in a fitness class.
    
    Validates:
    - Class exists and is upcoming
    - Slots are available
    - Client hasn't already booked this class
    
    Returns the created booking with class details.
    """
    # Step 1: Validate class exists
    fitness_class = crud.get_class_by_id(db, booking_data.class_id)
    if not fitness_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {booking_data.class_id} not found"
        )
    
    # Step 2: Check if class is upcoming (not in the past)
    if fitness_class.datetime_utc < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book a class that has already started or ended"
        )
    
    # Step 3: Check available slots
    if fitness_class.available_slots <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Class is fully booked",
                "class_name": fitness_class.name,
                "datetime": fitness_class.datetime_ist.isoformat()
            }
        )
    
    # Step 4: Check for duplicate booking
    email_normalized = booking_data.client_email.lower()
    if crud.check_existing_booking(db, booking_data.class_id, email_normalized):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "You have already booked this class",
                "class_name": fitness_class.name,
                "client_email": email_normalized
            }
        )
    
    # Step 5: Create the booking
    try:
        # Normalize email to lowercase for consistency
        booking_data.client_email = email_normalized
        new_booking = crud.create_booking(db, booking_data)
        
        return new_booking
        
    except Exception as e:
        # Rollback is handled automatically by SQLAlchemy
        print(f"Error creating booking: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the booking"
        )


# 3. GET /bookings - Get bookings by email
@router.get(
    "/bookings",
    response_model=schemas.BookingListResponse,
    summary="Get bookings by email",
    description="Returns all bookings made by a specific email address"
)
async def get_bookings(
    email: str = Depends(validate_email_query),
    db: Session = Depends(get_db)
):
    """
    Retrieve all bookings for a specific email address.
    
    - **email**: Email address to filter bookings (required)
    
    Returns bookings sorted by booking date (newest first).
    """
    try:
        # Normalize email for consistent querying
        email_normalized = email.lower()
        
        # Get bookings from database
        bookings = crud.get_bookings_by_email(db, email_normalized)
        
        # Return structured response
        return schemas.BookingListResponse(
            total=len(bookings),
            bookings=bookings
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (from validate_email_query)
        raise
    except Exception as e:
        print(f"Error fetching bookings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching bookings"
        )


# Health check endpoint
@router.get(
    "/health",
    response_model=schemas.MessageResponse,
    summary="Health check",
    description="Check if the API is running"
)
async def health_check():
    """Simple health check endpoint for monitoring."""
    return schemas.MessageResponse(
        message="API is healthy",
        details={
            "status": "online",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Optional: Add endpoint to get single class details
@router.get(
    "/classes/{class_id}",
    response_model=schemas.FitnessClassResponse,
    summary="Get class details",
    description="Get details of a specific fitness class"
)
async def get_class_details(
    class_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific fitness class."""
    fitness_class = crud.get_class_by_id(db, class_id)
    
    if not fitness_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {class_id} not found"
        )
    
    return fitness_class