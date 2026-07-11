import csv
from app.models import MealBooking, FoodWasteRecord, Feedback

def generate_bookings_csv(stream):
    """Writes all booking logs in CSV format to the provided stream."""
    writer = csv.writer(stream)
    # Header
    writer.writerow([
        'Booking ID', 'Student Name', 'Student Email', 
        'Meal Date', 'Meal Type', 'Status', 
        'Created At', 'Last Updated'
    ])
    
    bookings = MealBooking.query.order_by(MealBooking.date.desc(), MealBooking.meal_type.desc()).all()
    for b in bookings:
        writer.writerow([
            b.id,
            b.user.name,
            b.user.email,
            b.date.strftime("%Y-%m-%d"),
            b.meal_type.capitalize(),
            b.status.capitalize(),
            b.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            b.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        ])


def generate_waste_csv(stream):
    """Writes all food waste logs in CSV format to the provided stream."""
    writer = csv.writer(stream)
    # Header
    writer.writerow([
        'Record ID', 'Meal Date', 'Meal Type', 
        'Expected Attendance', 'Food Prepared (kg)', 
        'Food Consumed (kg)', 'Food Wasted (kg)', 
        'Waste Percentage (%)', 'Logged At'
    ])
    
    records = FoodWasteRecord.query.order_by(FoodWasteRecord.date.desc(), FoodWasteRecord.meal_type.desc()).all()
    for r in records:
        writer.writerow([
            r.id,
            r.date.strftime("%Y-%m-%d"),
            r.meal_type.capitalize(),
            r.expected_students,
            f"{r.food_prepared:.2f}",
            f"{r.food_consumed:.2f}",
            f"{r.food_wasted:.2f}",
            f"{r.waste_percentage:.2f}",
            r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])


def generate_feedback_csv(stream):
    """Writes all student feedback records in CSV format to the provided stream."""
    writer = csv.writer(stream)
    # Header
    writer.writerow([
        'Feedback ID', 'Student Name', 'Student Email', 
        'Meal Date', 'Meal Type', 'Rating (1-5)', 
        'Comment', 'Submitted At'
    ])
    
    feedbacks = Feedback.query.order_by(Feedback.date.desc(), Feedback.created_at.desc()).all()
    for f in feedbacks:
        writer.writerow([
            f.id,
            f.user.name,
            f.user.email,
            f.date.strftime("%Y-%m-%d"),
            f.meal_type.capitalize(),
            f.rating,
            f.comment or '',
            f.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
