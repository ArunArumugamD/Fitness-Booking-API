"""
SQLAlchemy ORM models define our database structure.
Each class represents a table in the database.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import pytz
from .config import IST


class FitnessClass(Base):
    """Model for fitness classes offered by the studio"""
    __tablename__ = "fitness_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Yoga", "Zumba", "HIIT"
    instructor = Column(String, nullable=False)
    
    # Store datetime in UTC in database, convert to IST when needed
    datetime_utc = Column(DateTime, nullable=False)
    
    # Total slots available for this class
    total_slots = Column(Integer, nullable=False)
    
    # Relationship to bookings (one-to-many)
    bookings = relationship("Booking", back_populates="fitness_class", cascade="all, delete-orphan")
    
    @property
    def datetime_ist(self):
        """Convert UTC datetime to IST for display"""
        if self.datetime_utc:
            # If datetime is naive (no timezone), assume it's UTC
            if self.datetime_utc.tzinfo is None:
                utc_dt = pytz.UTC.localize(self.datetime_utc)
            else:
                utc_dt = self.datetime_utc
            return utc_dt.astimezone(IST)
        return None
    
    @property
    def available_slots(self):
        """Calculate available slots by subtracting bookings from total"""
        return self.total_slots - len(self.bookings)
    
    def __repr__(self):
        return f"<FitnessClass {self.name} on {self.datetime_ist}>"


class Booking(Base):
    """Model for client bookings"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("fitness_classes.id"), nullable=False)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False, index=True)  # Index for faster queries
    
    # Timestamp when booking was made (UTC)
    booked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to fitness class (many-to-one)
    fitness_class = relationship("FitnessClass", back_populates="bookings")
    
    @property
    def booked_at_ist(self):
        """Convert booking timestamp to IST"""
        if self.booked_at:
            if self.booked_at.tzinfo is None:
                utc_dt = pytz.UTC.localize(self.booked_at)
            else:
                utc_dt = self.booked_at
            return utc_dt.astimezone(IST)
        return None
    
    def __repr__(self):
        return f"<Booking {self.client_name} for class {self.class_id}>"