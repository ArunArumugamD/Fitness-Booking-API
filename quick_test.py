"""
Quick test script to verify the API is working correctly.
Run this after starting the server to test basic functionality.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing Fitness Booking API...\n")
    
    # 1. Health Check
    print("1️⃣ Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()['message']}\n")
    
    # 2. Get Classes
    print("2️⃣ Testing Get Classes...")
    response = requests.get(f"{BASE_URL}/api/v1/classes")
    classes = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Found {classes['total']} classes")
    if classes['total'] > 0:
        first_class = classes['classes'][0]
        print(f"   First class: {first_class['name']} on {first_class['datetime_ist']}")
        class_id = first_class['id']
    print()
    
    # 3. Book a Class
    if classes['total'] > 0:
        print("3️⃣ Testing Book a Class...")
        booking_data = {
            "class_id": class_id,
            "client_name": "Test User",
            "client_email": "test@example.com"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/book",
            json=booking_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✅ Successfully booked class!")
        else:
            print(f"   ❌ Booking failed: {response.json()}")
        print()
    
    # 4. Get Bookings
    print("4️⃣ Testing Get Bookings...")
    response = requests.get(f"{BASE_URL}/api/v1/bookings?email=test@example.com")
    bookings = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Found {bookings['total']} bookings for test@example.com")
    
    print("\n✅ All tests completed!")
    print(f"\n📚 View API documentation at: {BASE_URL}/docs")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")