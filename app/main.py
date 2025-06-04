"""
Main FastAPI application setup.
This is the entry point for our API.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .database import engine, Base
from .api import routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created/verified")

# Create FastAPI instance
app = FastAPI(
    title=settings.app_name,
    description="API for booking fitness classes at our studio. Supports viewing classes and making bookings.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
)

# Add CORS middleware (configure based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to provide cleaner error messages.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


# Root endpoint
@app.get("/", response_model=dict)
async def root():
    """Welcome endpoint with API information."""
    return {
        "message": "Welcome to Fitness Studio Booking API",
        "documentation": "/docs",
        "health_check": "/api/v1/health",
        "version": "1.0.0"
    }


# Include API routes
app.include_router(routes.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info(f"{settings.app_name} started")
    logger.info(f"Timezone: {settings.timezone}")
    logger.info(f"Database: {settings.database_url}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run cleanup tasks."""
    logger.info(f"{settings.app_name} shutting down")


# Optional: Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions to prevent exposing internal errors.
    In production, you'd want to log these errors to a monitoring service.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later."
        }
    )