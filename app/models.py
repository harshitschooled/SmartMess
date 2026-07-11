from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize db object to be imported and bound to the application context
db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False) # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    bookings = db.relationship('MealBooking', backref='user', lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship('Feedback', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class MealBooking(db.Model):
    __tablename__ = 'meal_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False) # 'breakfast', 'lunch', 'dinner'
    status = db.Column(db.String(20), nullable=False) # 'eating', 'skipping'
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Enforce unique booking per user per date per meal_type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', 'meal_type', name='uq_user_meal_booking'),
    )

    def __repr__(self):
        return f"<MealBooking user_id={self.user_id} date={self.date} type={self.meal_type} status={self.status}>"


class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False) # 'breakfast', 'lunch', 'dinner'
    items = db.Column(db.Text, nullable=False) # Text containing items, e.g. "Idli, Sambar, Chutney"
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Enforce unique menu per date and meal type
    __table_args__ = (
        db.UniqueConstraint('date', 'meal_type', name='uq_menu_date_meal_type'),
    )

    def __repr__(self):
        return f"<Menu date={self.date} type={self.meal_type}>"


class FoodWasteRecord(db.Model):
    __tablename__ = 'food_waste_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False) # 'breakfast', 'lunch', 'dinner'
    expected_students = db.Column(db.Integer, nullable=False)
    food_prepared = db.Column(db.Float, nullable=False) # in kg
    food_consumed = db.Column(db.Float, nullable=False) # in kg
    food_wasted = db.Column(db.Float, nullable=False) # in kg, derived as prepared - consumed
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Unique constraint per date and meal type
    __table_args__ = (
        db.UniqueConstraint('date', 'meal_type', name='uq_waste_date_meal_type'),
    )

    @property
    def waste_percentage(self):
        if self.food_prepared > 0:
            return (self.food_wasted / self.food_prepared) * 100
        return 0.0

    def __repr__(self):
        return f"<FoodWasteRecord date={self.date} type={self.meal_type} wasted={self.food_wasted}kg>"


class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False) # 'breakfast', 'lunch', 'dinner'
    rating = db.Column(db.Integer, nullable=False) # rating from 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', 'meal_type', name='uq_feedback_user_date_meal'),
    )
    
    def __repr__(self):
        return f"<Feedback user_id={self.user_id} date={self.date} rating={self.rating}>"
