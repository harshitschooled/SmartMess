import pytest
import datetime
from app import create_app
from app.models import db, User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing convenience
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def seed_users(app):
    """Seed a student and an admin for authorization tests."""
    student = User(name="Test Student", email="student@test.com", role="student")
    student.set_password("student123")
    
    admin = User(name="Test Admin", email="admin@test.com", role="admin")
    admin.set_password("admin123")
    
    db.session.add(student)
    db.session.add(admin)
    db.session.commit()
    
    return student, admin
