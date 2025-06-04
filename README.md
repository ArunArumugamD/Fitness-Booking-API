# Fitness Studio Booking API

A robust booking API for a fitness studio built with FastAPI, featuring timezone management, comprehensive error handling, and clean architecture.

##  Features

- **View upcoming fitness classes** with real-time available slots
- **Book spots** in fitness classes with validation
- **View bookings** filtered by email address
- **IST timezone support** with automatic UTC conversion
- **Comprehensive error handling** for all edge cases
- **Auto-generated API documentation** via Swagger UI
- **SQLite database** for easy setup and portability
- **Full test coverage** with pytest

##  Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

##  Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/fitness-booking-api.git
cd fitness-booking-api
```

### 2. Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables (optional)
```bash
cp .env.example .env
# Edit .env if you want to change any settings
```

### 5. Initialize database with sample data
```bash
python seed_data.py
```

##  Running the Application

### Option 1: Using the run script
```bash
python run.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

##  API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

##  API Endpoints

### 1. Get Upcoming Classes
- **Endpoint:** `GET /api/v1/classes`
- **Description:** Returns all upcoming fitness classes with available slots
- **Query Parameters:** `skip` (default: 0), `limit` (default: 10, max: 100)

### 2. Book a Class
- **Endpoint:** `POST /api/v1/book`
- **Description:** Books a spot in a fitness class
- **Request Body:** `class_id`, `client_name`, `client_email`
- **Validations:** Class exists, has available slots, no duplicate bookings

### 3. Get Bookings by Email
- **Endpoint:** `GET /api/v1/bookings?email={email}`
- **Description:** Returns all bookings for a specific email address
- **Query Parameters:** `email` (required)

### Sample cURL Commands
```bash
# Get all classes
curl http://localhost:8000/api/v1/classes

# Book a class
curl -X POST http://localhost:8000/api/v1/book \
  -H "Content-Type: application/json" \
  -d '{"class_id": 1, "client_name": "John Doe", "client_email": "john@example.com"}'

# Get bookings
curl http://localhost:8000/api/v1/bookings?email=john@example.com
```

##  Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=app --cov-report=html
```

### Quick API test
```bash
python quick_test.py
```

##  Sample Postman Collection

A Postman collection is included in `postman_collection.json`. Import it into Postman to test all endpoints easily.


##  Error Handling

- **400**: Invalid requests (booking past classes)
- **404**: Resource not found (invalid class ID)
- **409**: Conflicts (double booking, full class)
- **422**: Validation errors (invalid email format)
- **500**: Server errors with safe error messages

##  Technical Implementation

- **Timezone Management**: UTC storage with automatic IST conversion
- **Real-time Availability**: Dynamic slot calculation prevents overbooking
- **Data Validation**: Pydantic schemas with email validation and sanitization
- **Clean Architecture**: Separated models, schemas, CRUD, and routes with dependency injection
- **Type Safety**: Full type hints for better IDE support and fewer bugs

##  Assignment Completion

All requirements implemented:
-  GET /classes, POST /book, GET /bookings endpoints
-  SQLite with IST timezone management
-  Comprehensive error handling & validation
-  Clean, modular, documented code
-  Unit tests, sample data, setup instructions
