import pytest
import datetime
from app.models import FoodWasteRecord, db

def test_food_waste_record_creation_and_derivation(client, seed_users, app):
    # Log in as Admin
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'admin123'})
    
    target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # Save a valid food waste record
    response = client.post('/admin/waste/new', data={
        'date': target_date,
        'meal_type': 'lunch',
        'food_prepared': '100.0',
        'food_consumed': '85.0'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"logged successfully" in response.data
    
    # Verify in DB and check derived values
    with app.app_context():
        record = FoodWasteRecord.query.filter_by(meal_type='lunch').first()
        assert record is not None
        assert record.food_prepared == 100.0
        assert record.food_consumed == 85.0
        assert record.food_wasted == 15.0  # Derived: 100 - 85
        assert record.waste_percentage == 15.0  # Derived: 15 / 100 * 100

def test_food_waste_validation_consumed_exceeds_prepared(client, seed_users):
    # Log in as Admin
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'admin123'})
    
    target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # Consumed exceeds Prepared (85 prepared, 100 consumed)
    response = client.post('/admin/waste/new', data={
        'date': target_date,
        'meal_type': 'lunch',
        'food_prepared': '85.0',
        'food_consumed': '100.0'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Consumed food cannot exceed prepared food" in response.data

def test_food_waste_negative_values(client, seed_users):
    # Log in as Admin
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'admin123'})
    
    target_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # Negative prepared value
    response = client.post('/admin/waste/new', data={
        'date': target_date,
        'meal_type': 'lunch',
        'food_prepared': '-50.0',
        'food_consumed': '10.0'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"cannot be negative" in response.data

def test_waste_percentage_division_by_zero(app):
    # Directly test the waste percentage property on a 0-prepared record
    with app.app_context():
        record = FoodWasteRecord(
            date=datetime.date.today(),
            meal_type='dinner',
            expected_students=0,
            food_prepared=0.0,
            food_consumed=0.0,
            food_wasted=0.0
        )
        assert record.waste_percentage == 0.0
