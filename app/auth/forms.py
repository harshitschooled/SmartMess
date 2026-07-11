from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters.")
    ])
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('This email address is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Log In')
