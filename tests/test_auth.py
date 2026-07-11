import datetime
import pytest
from app import create_app
from app.models import Feedback, User, db

def test_student_registration(client, app):
    # Register student
    response = client.post('/auth/register', data={
        'name': 'Bob Student',
        'email': 'bob@college.edu',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Account created successfully" in response.data
    
    with app.app_context():
        user = User.query.filter_by(email='bob@college.edu').first()
        assert user is not None
        assert user.name == 'Bob Student'
        assert user.role == 'student'
        assert user.check_password('password123') is True

def test_duplicate_registration_fails(client, seed_users):
    # Attempt to register with student@test.com (already seeded)
    response = client.post('/auth/register', data={
        'name': 'Duplicate User',
        'email': 'student@test.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"already registered" in response.data

def test_login_and_logout(client, seed_users):
    # Log in student
    response = client.post('/auth/login', data={
        'email': 'student@test.com',
        'password': 'student123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Welcome back, Test Student" in response.data
    
    # Log out
    response_logout = client.get('/auth/logout', follow_redirects=True)
    assert response_logout.status_code == 200
    assert b"logged out successfully" in response_logout.data

def test_login_invalid_password(client, seed_users):
    response = client.post('/auth/login', data={
        'email': 'student@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_duplicate_feedback_is_rejected(client, seed_users, app):
    client.post('/auth/login', data={'email': 'student@test.com', 'password': 'student123'})

    target_date = datetime.date.today().strftime('%Y-%m-%d')

    response = client.post('/student/feedback', data={
        'date': target_date,
        'meal_type': 'lunch',
        'rating': '4',
        'comment': 'Great meal'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Thank you for your feedback" in response.data

    duplicate_response = client.post('/student/feedback', data={
        'date': target_date,
        'meal_type': 'lunch',
        'rating': '5',
        'comment': 'Second submission'
    }, follow_redirects=True)

    assert duplicate_response.status_code == 200
    assert b"already submitted feedback" in duplicate_response.data

    with app.app_context():
        student = seed_users[0]
        count = Feedback.query.filter_by(
            user_id=student.id,
            date=datetime.date.today(),
            meal_type='lunch'
        ).count()
        assert count == 1


def test_missing_secret_key_raises_runtime_error():
    class MissingSecretKeyConfig:
        SECRET_KEY = None
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        TESTING = True

    with pytest.raises(RuntimeError, match='SECRET_KEY'):
        create_app(MissingSecretKeyConfig)
