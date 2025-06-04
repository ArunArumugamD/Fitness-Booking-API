"""
Basic API tests using pytest and FastAPI's test client.
Run with: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import FitnessClass
from app.utils.timezone import ist_to_utc
from app.config import IST


# Create test client
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_classes(db_session):
    """Create sample fitness classes for testing."""
    now_ist = datetime.now(IST)
    
    classes = [
        FitnessClass(
            name="Test Yoga",
            instructor="Test Instructor",
            datetime_utc=ist_to_utc(now_ist + timedelta(days=1)),
            total_slots=10
        ),
        FitnessClass(
            name="Test HIIT",
            instructor="Test Trainer",
            datetime_utc=ist_to_utc(now_ist + timedelta(days=2)),
            total_slots=1  # Only 1 slot for testing full booking
        )
    ]
    
    for cls in classes:
        db_session.add(cls)
    db_session.commit()
    
    return classes


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "API is healthy"
        assert "timestamp" in data["details"]


class TestGetClasses:
    """Test GET /classes endpoint."""
    
    def test_get_classes_empty(self, setup_database):
        response = client.get("/api/v1/classes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["classes"] == []
    
    def test_get_classes_with_data(self, setup_database, sample_classes):
        response = client.get("/api/v1/classes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["classes"]) == 2
        
        # Check first class
        first_class = data["classes"][0]
        assert first_class["name"] == "Test Yoga"
        assert first_class["available_slots"] == 10
    
    def test_get_classes_pagination(self, setup_database, sample_classes):
        # Test with limit
        response = client.get("/api/v1/classes?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["classes"]) == 1
        
        # Test with skip
        response = client.get("/api/v1/classes?skip=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["classes"]) == 1
        assert data["classes"][0]["name"] == "Test HIIT"


class TestCreateBooking:
    """Test POST /book endpoint."""
    
    def test_create_booking_success(self, setup_database, sample_classes):
        booking_data = {
            "class_id": sample_classes[0].id,
            "client_name": "John Doe",
            "client_email": "john@example.com"
        }
        
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 201
        data = response.json()
        assert data["client_name"] == "John Doe"
        assert data["client_email"] == "john@example.com"
        assert data["fitness_class"]["name"] == "Test Yoga"
    
    def test_create_booking_class_not_found(self, setup_database):
        booking_data = {
            "class_id": 9999,
            "client_name": "John Doe",
            "client_email": "john@example.com"
        }
        
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_create_booking_duplicate(self, setup_database, sample_classes):
        booking_data = {
            "class_id": sample_classes[0].id,
            "client_name": "John Doe",
            "client_email": "john@example.com"
        }
        
        # First booking should succeed
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 201
        
        # Second booking should fail
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 409
        assert "already booked" in response.json()["detail"]["error"]
    
    def test_create_booking_full_class(self, setup_database, sample_classes):
        # Book the only available slot
        booking_data = {
            "class_id": sample_classes[1].id,  # HIIT class with 1 slot
            "client_name": "First User",
            "client_email": "first@example.com"
        }
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 201
        
        # Try to book when full
        booking_data["client_email"] = "second@example.com"
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 409
        assert "fully booked" in response.json()["detail"]["error"]
    
    def test_create_booking_invalid_email(self, setup_database, sample_classes):
        booking_data = {
            "class_id": sample_classes[0].id,
            "client_name": "John Doe",
            "client_email": "invalid-email"
        }
        
        response = client.post("/api/v1/book", json=booking_data)
        assert response.status_code == 422
        assert "email" in str(response.json()["errors"])


class TestGetBookings:
    """Test GET /bookings endpoint."""
    
    def test_get_bookings_by_email(self, setup_database, sample_classes):
        # Create a booking first
        booking_data = {
            "class_id": sample_classes[0].id,
            "client_name": "Jane Doe",
            "client_email": "jane@example.com"
        }
        client.post("/api/v1/book", json=booking_data)
        
        # Get bookings
        response = client.get("/api/v1/bookings?email=jane@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["bookings"][0]["client_email"] == "jane@example.com"
    
    def test_get_bookings_no_email(self, setup_database):
        response = client.get("/api/v1/bookings")
        assert response.status_code == 422
    
    def test_get_bookings_empty_result(self, setup_database):
        response = client.get("/api/v1/bookings?email=nonexistent@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["bookings"] == []