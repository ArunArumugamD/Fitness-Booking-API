"""
Shared dependencies for API routes.
Dependencies in FastAPI are reusable functions that can be injected into routes.
"""
from typing import Optional
from fastapi import Query, HTTPException, status


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return")
):
    """
    Common pagination parameters for list endpoints.
    
    Query parameters are automatically validated by FastAPI.
    - ge=0: greater than or equal to 0
    - le=100: less than or equal to 100
    """
    return {"skip": skip, "limit": limit}


def validate_email_query(
    email: str = Query(..., description="Email address to filter bookings")
):
    """
    Validate email query parameter.
    The '...' means this parameter is required.
    """
    if not email or len(email.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email parameter is required and cannot be empty"
        )
    return email.strip().lower()