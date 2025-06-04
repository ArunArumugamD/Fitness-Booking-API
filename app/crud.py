"""
CRUD (Create, Read, Update, Delete) operations.
This module contains all database operations, keeping them separate from API logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from . import models, schemas
from typing import List, Optional


def get_upcoming_classes(db: Session, skip: int = 0, limit: int = 100) -> List[models.FitnessClass]:
    """
    Get all upcoming fitness classes (classes scheduled after current time).
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    
    Returns:
        List of upcoming fitness classes
    """
    current_time_utc = datetime.utcnow()
    
    return db.query(models.FitnessClass)\
        .filter(models.FitnessClass.datetime_utc > current_time_utc)\
        .order_by(models.FitnessClass.datetime_utc)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_class_by_id(db: Session, class_id: int) -> Optional[models.FitnessClass]:
    """Get a specific fitness class by ID"""
    return db.query(models.FitnessClass).filter(models.FitnessClass.id == class_id).first()


def create_booking(db: Session, booking: schemas.BookingCreate) -> models.Booking:
    """
    Create a new booking.
    
    Args:
        db: Database session
        booking: Booking data from request
    
    Returns:
        Created booking object
    
    Note: This doesn't check for available slots - that should be done in the API layer
    """
    db_booking = models.Booking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)  # Refresh to get the generated ID and relationships
    return db_booking


def get_bookings_by_email(db: Session, email: str) -> List[models.Booking]:
    """
    Get all bookings for a specific email address.
    
    Args:
        db: Database session
        email: Client's email address
    
    Returns:
        List of bookings for the email
    """
    return db.query(models.Booking)\
        .filter(models.Booking.client_email == email)\
        .order_by(models.Booking.booked_at.desc())\
        .all()


def check_existing_booking(db: Session, class_id: int, email: str) -> bool:
    """
    Check if a client has already booked a specific class.
    
    Args:
        db: Database session
        class_id: ID of the fitness class
        email: Client's email address
    
    Returns:
        True if booking exists, False otherwise
    """
    existing = db.query(models.Booking)\
        .filter(and_(
            models.Booking.class_id == class_id,
            models.Booking.client_email == email
        ))\
        .first()
    
    return existing is not None