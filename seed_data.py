"""
Script to populate the database with sample fitness classes.
Run this after setting up the application to add test data.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal, engine, Base
from app.models import FitnessClass
from app.utils.timezone import ist_to_utc
from app.config import IST

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def create_sample_classes():
    """Create sample fitness classes for testing."""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(FitnessClass).delete()
        db.commit()
        
        # Get current time in IST
        now_ist = datetime.now(IST)
        
        # Sample classes data
        sample_classes = [
            # Today's classes
            {
                "name": "Morning Yoga",
                "instructor": "Priya Sharma",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=6, minute=30, second=0, microsecond=0) + timedelta(days=1)),
                "total_slots": 20
            },
            {
                "name": "HIIT Workout",
                "instructor": "Raj Kumar",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=7, minute=30, second=0, microsecond=0) + timedelta(days=1)),
                "total_slots": 15
            },
            # Tomorrow's classes
            {
                "name": "Evening Zumba",
                "instructor": "Anita Desai",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=2)),
                "total_slots": 25
            },
            {
                "name": "Power Yoga",
                "instructor": "Priya Sharma",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=19, minute=30, second=0, microsecond=0) + timedelta(days=2)),
                "total_slots": 20
            },
            # Weekend classes
            {
                "name": "Weekend HIIT",
                "instructor": "Raj Kumar",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=3)),
                "total_slots": 30
            },
            {
                "name": "Relaxation Yoga",
                "instructor": "Priya Sharma",
                "datetime_utc": ist_to_utc(now_ist.replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=3)),
                "total_slots": 25
            },
        ]
        
        # Create class instances
        for class_data in sample_classes:
            fitness_class = FitnessClass(**class_data)
            db.add(fitness_class)
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Successfully created {len(sample_classes)} sample fitness classes")
        
        # Display created classes
        print("\nCreated classes:")
        classes = db.query(FitnessClass).all()
        for cls in classes:
            print(f"- {cls.name} by {cls.instructor} on {cls.datetime_ist.strftime('%Y-%m-%d %H:%M IST')}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_classes()