import pytest
import datetime
from app.models import MealBooking, db
from app.services import booking_service

def test_meal_booking_creation_and_update(client, seed_users, app):
    # Log in student
    client.post('/auth/login', data={'email': 'student@test.com', 'password': 'student123'})
    
    # Target date for booking (e.g. tomorrow)
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    # Mock current time: set it to 10:00 AM today (before any tomorrow breakfast deadlines)
    now_today = datetime.datetime.combine(datetime.date.today(), datetime.time(10, 0))
    booking_service.set_test_time(now_today)
    
    # Create booking for breakfast tomorrow
    response = client.post('/student/book', data={
        'date': tomorrow_str,
        'meal_type': 'breakfast',
        'status': 'eating'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Successfully booked Breakfast as &#34;Eating&#34;" in response.data
    
    # Verify DB state
    with app.app_context():
        student = seed_users[0]
        b = MealBooking.query.filter_by(user_id=student.id, date=tomorrow, meal_type='breakfast').first()
        assert b is not None
        assert b.status == 'eating'
        
    # Update same booking to 'skipping' (idempotent / duplicate prevention check)
    response_update = client.post('/student/book', data={
        'date': tomorrow_str,
        'meal_type': 'breakfast',
        'status': 'skipping'
    }, follow_redirects=True)
    
    assert response_update.status_code == 200
    assert b"Successfully updated Breakfast booking to &#34;Skipping&#34;" in response_update.data
    
    with app.app_context():
        student = seed_users[0]
        # Count should remain 1 (no duplicate generated)
        cnt = MealBooking.query.filter_by(user_id=student.id, date=tomorrow, meal_type='breakfast').count()
        assert cnt == 1
        b_updated = MealBooking.query.filter_by(user_id=student.id, date=tomorrow, meal_type='breakfast').first()
        assert b_updated.status == 'skipping'

def test_booking_deadline_validation(client, seed_users, app):
    # Log in student
    client.post('/auth/login', data={'email': 'student@test.com', 'password': 'student123'})
    
    # Target date for booking: tomorrow
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    # Breakfast deadline closes at 9:00 PM on the previous day (today 21:00)
    
    # Test case 1: Open (Today at 8:00 PM)
    open_time = datetime.datetime.combine(datetime.date.today(), datetime.time(20, 0))
    booking_service.set_test_time(open_time)
    
    res_open = client.post('/student/book', data={
        'date': tomorrow_str,
        'meal_type': 'breakfast',
        'status': 'eating'
    }, follow_redirects=True)
    assert b"Successfully booked" in res_open.data or b"Successfully updated" in res_open.data
    
    # Test case 2: Closed (Today at 10:00 PM - past 9:00 PM)
    closed_time = datetime.datetime.combine(datetime.date.today(), datetime.time(22, 0))
    booking_service.set_test_time(closed_time)
    
    res_closed = client.post('/student/book', data={
        'date': tomorrow_str,
        'meal_type': 'breakfast',
        'status': 'skipping'
    }, follow_redirects=True)
    
    assert b"Booking deadline passed" in res_closed.data

    # Test case 3: Exactly at the deadline should also be closed
    deadline_time = datetime.datetime.combine(datetime.date.today(), datetime.time(21, 0))
    booking_service.set_test_time(deadline_time)

    res_exact_deadline = client.post('/student/book', data={
        'date': tomorrow_str,
        'meal_type': 'breakfast',
        'status': 'eating'
    }, follow_redirects=True)

    assert b"Booking deadline passed" in res_exact_deadline.data
    
    # Cleanup test time
    booking_service.set_test_time(None)
