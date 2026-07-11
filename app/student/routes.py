import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.models import db, User, MealBooking, Menu, Feedback
from flask import Blueprint
student_bp = Blueprint('student', __name__)
from app.auth.routes import student_required
from app.services import booking_service

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    today = booking_service.get_current_time().date()
    
    # Fetch today's menus
    menus_list = Menu.query.filter_by(date=today).all()
    menus = {m.meal_type: m.items for m in menus_list}
    
    # Fetch today's bookings for the user
    user_bookings = MealBooking.query.filter_by(user_id=current_user.id, date=today).all()
    bookings = {b.meal_type: b.status for b in user_bookings}
    
    # Check if booking is open for each meal today
    deadlines_open = {
        'breakfast': booking_service.is_booking_open(today, 'breakfast'),
        'lunch': booking_service.is_booking_open(today, 'lunch'),
        'dinner': booking_service.is_booking_open(today, 'dinner')
    }
    
    # Recent bookings (past 10 bookings)
    recent_bookings = MealBooking.query.filter_by(user_id=current_user.id)\
        .order_by(MealBooking.date.desc(), MealBooking.meal_type.desc())\
        .limit(10).all()
        
    # Recent feedbacks submitted by this student
    recent_feedbacks = Feedback.query.filter_by(user_id=current_user.id)\
        .order_by(Feedback.created_at.desc())\
        .limit(5).all()
        
    return render_template(
        'student/dashboard.html',
        today=today,
        menus=menus,
        bookings=bookings,
        deadlines_open=deadlines_open,
        recent_bookings=recent_bookings,
        recent_feedbacks=recent_feedbacks
    )


@student_bp.route('/book', methods=['POST'])
@login_required
@student_required
def book():
    date_str = request.form.get('date')
    meal_type = request.form.get('meal_type')
    status = request.form.get('status') # 'eating' or 'skipping'
    
    if not date_str or not meal_type or not status:
        flash('Invalid booking parameters.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    try:
        booking_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    if meal_type not in ['breakfast', 'lunch', 'dinner']:
        flash('Invalid meal type.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    if status not in ['eating', 'skipping']:
        flash('Invalid booking status.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # BACKEND DEADLINE ENFORCEMENT
    if not booking_service.is_booking_open(booking_date, meal_type):
        deadline_dt = booking_service.get_deadline_for_meal(booking_date, meal_type)
        flash(f'Booking deadline passed! Changes closed at {deadline_dt.strftime("%I:%M %p on %b %d")}.', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # Create or update booking logic
    booking = MealBooking.query.filter_by(
        user_id=current_user.id,
        date=booking_date,
        meal_type=meal_type
    ).first()
    
    if booking:
        booking.status = status
        booking.updated_at = booking_service.get_current_time()
        flash(f'Successfully updated {meal_type.capitalize()} booking to "{status.capitalize()}".', 'success')
    else:
        booking = MealBooking(
            user_id=current_user.id,
            date=booking_date,
            meal_type=meal_type,
            status=status
        )
        db.session.add(booking)
        flash(f'Successfully booked {meal_type.capitalize()} as "{status.capitalize()}".', 'success')
        
    db.session.commit()
    return redirect(url_for('student.dashboard'))


@student_bp.route('/history')
@login_required
@student_required
def booking_history():
    # Show all past and future bookings of the student
    bookings = MealBooking.query.filter_by(user_id=current_user.id)\
        .order_by(MealBooking.date.desc(), MealBooking.meal_type.desc())\
        .all()
    return render_template('student/booking_history.html', bookings=bookings)


@student_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
@student_required
def feedback():
    if request.method == 'POST':
        date_str = request.form.get('date')
        meal_type = request.form.get('meal_type')
        rating_str = request.form.get('rating')
        comment = request.form.get('comment', '').strip()
        
        if not date_str or not meal_type or not rating_str:
            flash('All feedback fields are required.', 'danger')
            return redirect(url_for('student.feedback'))
            
        try:
            feedback_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('student.feedback'))
            
        if meal_type not in ['breakfast', 'lunch', 'dinner']:
            flash('Invalid meal type.', 'danger')
            return redirect(url_for('student.feedback'))
            
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                raise ValueError()
        except ValueError:
            flash('Rating must be an integer between 1 and 5.', 'danger')
            return redirect(url_for('student.feedback'))
            
        # Optional validation: only allow feedback for past or present days
        today = booking_service.get_current_time().date()
        if feedback_date > today:
            flash('You cannot submit feedback for a future date.', 'danger')
            return redirect(url_for('student.feedback'))
            
        existing_feedback = Feedback.query.filter_by(
            user_id=current_user.id,
            date=feedback_date,
            meal_type=meal_type
        ).first()
        if existing_feedback:
            flash('You have already submitted feedback for this meal.', 'warning')
            return redirect(url_for('student.dashboard'))

        feedback_record = Feedback(
            user_id=current_user.id,
            date=feedback_date,
            meal_type=meal_type,
            rating=rating,
            comment=comment if comment else None
        )
        db.session.add(feedback_record)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('You have already submitted feedback for this meal.', 'warning')
            return redirect(url_for('student.dashboard'))
        
        flash('Thank you for your feedback! It has been recorded.', 'success')
        return redirect(url_for('student.dashboard'))
        
    # GET request prefill fields if sent in query parameters
    prefill_date = request.args.get('date', '')
    prefill_meal = request.args.get('meal_type', '')
    return render_template('student/feedback.html', prefill_date=prefill_date, prefill_meal=prefill_meal)
