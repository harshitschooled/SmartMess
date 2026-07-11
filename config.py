import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database config
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Flask-SQLAlchemy expects sqlite:////absolute/path on windows sometimes,
        # but standard sqlite:///smartmess.db is relative to project root.
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'smartmess.db')}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Booking deadlines configurations
    # Format is HH:MM in 24-hour style
    # Breakfast closes at 9:00 PM (21:00) on the previous day
    # Lunch closes at 9:00 AM (09:00) on the same day
    # Dinner closes at 3:00 PM (15:00) on the same day
    BREAKFAST_DEADLINE_TIME = "21:00"
    LUNCH_DEADLINE_TIME = "09:00"
    DINNER_DEADLINE_TIME = "15:00"
    
    # Timezone note: The system assumes the local time of the hosting environment.
