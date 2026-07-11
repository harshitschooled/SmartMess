import datetime
import random
import sys
import os

# Append the project root to sys.path to allow importing app package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User, MealBooking, Menu, FoodWasteRecord, Feedback

def seed_database():
    app = create_app()
    with app.app_context():
        print("Resetting database (dropping all tables)...")
        db.drop_all()
        db.create_all()
        
        print("Seeding database...")
        
        # 1. Seed Admin
        admin = User(name="Mess Administrator", email="admin@college.edu", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        
        # 2. Seed 10 Students
        students = []
        names = [
            "Aarav Sharma", "Ananya Iyer", "Vihaan Patel", "Diya Malhotra", 
            "Kabir Joshi", "Ishita Sen", "Aditya Rao", "Riya Verma", 
            "Sai Reddy", "Meera Nair"
        ]
        
        for i, name in enumerate(names, 1):
            email = f"student{i}@college.edu"
            student = User(name=name, email=email, role="student")
            student.set_password("student123")
            db.session.add(student)
            students.append(student)
            
        db.session.commit()
        print(f"Created 1 admin and {len(students)} student accounts.")
        
        # Date configuration: last 20 days to next 10 days (total 30 days)
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=20)
        end_date = today + datetime.timedelta(days=10)
        
        total_days = (end_date - start_date).days + 1
        date_list = [start_date + datetime.timedelta(days=x) for x in range(total_days)]
        
        # 3. Seed Menus (from past 14 days to next 14 days = 28 days or all 30 days)
        menu_items = {
            'breakfast': [
                "Idli, Sambar, Coconut Chutney",
                "Aloo Paratha, Butter, Curd",
                "Bread Toast, Butter, Jam, Boiled Egg",
                "Poha, Sev, Hot Milk",
                "Masala Dosa, Tomato Chutney, Sambar",
                "Upma, Coconut Chutney, Banana",
                "Puri, Sagogi / Potato Bhaji"
            ],
            'lunch': [
                "Rice, Dal Fry, Bhindi Fry, Curd, Roti",
                "Veg Biryani, Raita, Papad, Salad",
                "Rice, Sambar, Cabbage Thoran, Fried Fish / Potato Fry",
                "Jeera Rice, Paneer Butter Masala, Roti, Salad",
                "Rice, Rajma Masala, Aloo Gobi, Buttermilk",
                "Rice, Chicken Curry / Mushroom Masala, Roti, Curd",
                "Rice, Kadhi Pakora, Baingan Bharta, Salad"
            ],
            'dinner': [
                "Roti, Paneer Bhurji, Dal Tadka, Rice",
                "Egg Curry / Egg Bhurji, Rice, Roti, Salad",
                "Roti, Mix Veg Korma, Dal Makhani, Rice",
                "Gobi Manchurian, Veg Fried Rice, Soup",
                "Roti, Chicken Masala / Soya Chunks Curry, Rice, Salad",
                "Roti, Aloo Capsicum Dry, Yellow Dal, Rice",
                "Pav Bhaji, Pulav, Onion Raita"
            ]
        }
        
        menus_seeded = 0
        for date_val in date_list:
            for meal in ['breakfast', 'lunch', 'dinner']:
                # Select a random menu from template based on date hash to be deterministic but varied
                idx = (date_val.day + len(meal)) % 7
                items = menu_items[meal][idx]
                
                menu = Menu(date=date_val, meal_type=meal, items=items)
                db.session.add(menu)
                menus_seeded += 1
                
        db.session.commit()
        print(f"Seeded {menus_seeded} menu records across 30 days.")
        
        # 4. Seed Meal Bookings (last 20 days to today)
        # Students confirm eating or skipping
        bookings_seeded = 0
        # We only book for past days + today
        booking_dates = [d for d in date_list if d <= today]
        
        for date_val in booking_dates:
            for student in students:
                for meal in ['breakfast', 'lunch', 'dinner']:
                    # 75% chance eating, 25% skipping
                    status = 'eating' if random.random() < 0.78 else 'skipping'
                    
                    booking = MealBooking(
                        user_id=student.id,
                        date=date_val,
                        meal_type=meal,
                        status=status,
                        created_at=datetime.datetime.combine(date_val - datetime.timedelta(days=1), datetime.time(18, 0))
                    )
                    db.session.add(booking)
                    bookings_seeded += 1
                    
        db.session.commit()
        print(f"Seeded {bookings_seeded} booking records for students.")
        
        # 5. Seed Food Waste Records (last 20 days to yesterday)
        # Expected count comes from 'eating' bookings
        waste_seeded = 0
        waste_dates = [d for d in booking_dates if d < today]
        
        for date_val in waste_dates:
            for meal in ['breakfast', 'lunch', 'dinner']:
                expected_count = MealBooking.query.filter_by(
                    date=date_val,
                    meal_type=meal,
                    status='eating'
                ).count()
                
                if expected_count > 0:
                    # Let's say we prepare 0.4kg of food per expected student
                    prepared = round(expected_count * 0.4, 2)
                    # Consumption is 80% to 95% of prepared
                    consumption_pct = random.uniform(0.78, 0.95)
                    consumed = round(prepared * consumption_pct, 2)
                    wasted = round(prepared - consumed, 2)
                    
                    record = FoodWasteRecord(
                        date=date_val,
                        meal_type=meal,
                        expected_students=expected_count,
                        food_prepared=prepared,
                        food_consumed=consumed,
                        food_wasted=wasted,
                        created_at=datetime.datetime.combine(date_val, datetime.time(22, 0))
                    )
                    db.session.add(record)
                    waste_seeded += 1
                    
        db.session.commit()
        print(f"Seeded {waste_seeded} food waste logs (in kg).")
        
        # 6. Seed Feedbacks (last 15 days to yesterday)
        feedback_comments = {
            1: ["Food was extremely salty today.", "Very poor taste.", "Rotis were completely burnt.", "Uncooked dal."],
            2: ["Spice levels were too high.", "Food was cold when served.", "Portion size was too small.", "Need better hygiene."],
            3: ["Average food.", "Okay taste, nothing special.", "Curry was okay, but rotis could be softer.", "Average quality."],
            4: ["Good food today!", "Loved the paneer curry.", "Clean service and tasty meals.", "Nice taste and fresh fruits."],
            5: ["Excellent meal! Highly satisfied.", "Biryani was top-notch!", "Best breakfast this week.", "Perfect taste and quantity."]
        }
        
        feedback_seeded = 0
        feedback_dates = [d for d in waste_dates if d > today - datetime.timedelta(days=15)]
        
        for date_val in feedback_dates:
            # Randomly select a few students to submit feedback
            submitting_students = random.sample(students, k=random.randint(1, 4))
            for student in submitting_students:
                meal = random.choice(['breakfast', 'lunch', 'dinner'])
                
                # Verify if student had an 'eating' booking on that date
                booking = MealBooking.query.filter_by(user_id=student.id, date=date_val, meal_type=meal).first()
                if booking and booking.status == 'eating':
                    rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.25, 0.4, 0.2])[0]
                    comment = random.choice(feedback_comments[rating]) if random.random() < 0.7 else None
                    
                    feedback_obj = Feedback(
                        user_id=student.id,
                        date=date_val,
                        meal_type=meal,
                        rating=rating,
                        comment=comment,
                        created_at=datetime.datetime.combine(date_val, datetime.time(21, 30))
                    )
                    db.session.add(feedback_obj)
                    feedback_seeded += 1
                    
        db.session.commit()
        print(f"Seeded {feedback_seeded} student feedbacks.")
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
