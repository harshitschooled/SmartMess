import datetime
from flask import current_app

# Allow test code to mock or override current time
_test_current_time = None

def set_test_time(dt_value):
    """Utility function to set an override datetime for unit testing deadlines."""
    global _test_current_time
    _test_current_time = dt_value

def get_current_time():
    """Returns the current local system datetime, or the overridden test datetime."""
    global _test_current_time
    if _test_current_time is not None:
        return _test_current_time
    return datetime.datetime.now()

def get_deadline_for_meal(date_val, meal_type):
    """
    Returns a datetime object representing the booking deadline for a specific date and meal type.
    
    Deadlines:
    - breakfast: 9:00 PM (21:00) on the previous day.
    - lunch: 9:00 AM (09:00) on the same day.
    - dinner: 3:00 PM (15:00) on the same day.
    """
    # Standardize date_val if it comes in as a string
    if isinstance(date_val, str):
        date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d").date()
    elif isinstance(date_val, datetime.datetime):
        date_val = date_val.date()
        
    if meal_type == 'breakfast':
        # Closes at 9:00 PM of previous day
        target_date = date_val - datetime.timedelta(days=1)
        # Parse from config or fallback
        time_str = current_app.config.get('BREAKFAST_DEADLINE_TIME', '21:00')
    elif meal_type == 'lunch':
        # Closes at 9:00 AM of same day
        target_date = date_val
        time_str = current_app.config.get('LUNCH_DEADLINE_TIME', '09:00')
    elif meal_type == 'dinner':
        # Closes at 3:00 PM of same day
        target_date = date_val
        time_str = current_app.config.get('DINNER_DEADLINE_TIME', '15:00')
    else:
        raise ValueError(f"Invalid meal_type: {meal_type}")
        
    hour, minute = map(int, time_str.split(':'))
    deadline_time = datetime.time(hour=hour, minute=minute)
    return datetime.datetime.combine(target_date, deadline_time)

def is_booking_open(date_val, meal_type):
    """
    Returns True only if the booking is still before the deadline.
    Bookings close exactly at the configured deadline time.
    """
    now = get_current_time()
    deadline = get_deadline_for_meal(date_val, meal_type)
    return now < deadline
