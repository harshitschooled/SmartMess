from collections import defaultdict
from sqlalchemy import func
from app.models import db, User, MealBooking, FoodWasteRecord, Feedback

def get_analytics_data():
    """
    Computes aggregates and formats data for Chart.js and admin statistics.
    Returns a dictionary of metrics.
    """
    # 1. Average rating per meal type
    ratings_query = db.session.query(
        Feedback.meal_type,
        func.avg(Feedback.rating)
    ).group_by(Feedback.meal_type).all()
    avg_ratings = {meal: round(float(avg), 2) for meal, avg in ratings_query}
    
    # Fill in default values if not present
    for meal in ['breakfast', 'lunch', 'dinner']:
        if meal not in avg_ratings:
            avg_ratings[meal] = 0.0

    # 2. Average waste percentage (Total wasted / Total prepared * 100)
    waste_totals = db.session.query(
        func.sum(FoodWasteRecord.food_prepared),
        func.sum(FoodWasteRecord.food_wasted)
    ).first()
    
    total_prep = float(waste_totals[0]) if waste_totals[0] else 0.0
    total_waste = float(waste_totals[1]) if waste_totals[1] else 0.0
    avg_waste_pct = round((total_waste / total_prep * 100), 2) if total_prep > 0 else 0.0

    # 3. Most skipped meal type
    skipping_query = db.session.query(
        MealBooking.meal_type,
        func.count(MealBooking.id)
    ).filter_by(status='skipping').group_by(MealBooking.meal_type).all()
    
    skipping_counts = {meal: count for meal, count in skipping_query}
    most_skipped_meal = "None"
    max_skip = -1
    for meal in ['breakfast', 'lunch', 'dinner']:
        cnt = skipping_counts.get(meal, 0)
        if cnt > max_skip:
            max_skip = cnt
            most_skipped_meal = meal
            
    if max_skip == 0:
        most_skipped_meal = "None"

    # 4. Daily attendance trends (last 14 days)
    # Group by date and status
    attendance_trend = db.session.query(
        MealBooking.date,
        MealBooking.status,
        func.count(MealBooking.id)
    ).group_by(MealBooking.date, MealBooking.status)\
     .order_by(MealBooking.date.asc())\
     .all()
     
    # Format: { 'YYYY-MM-DD': { 'eating': X, 'skipping': Y } }
    daily_data = defaultdict(lambda: {'eating': 0, 'skipping': 0})
    for date_val, status, count in attendance_trend:
        date_str = date_val.strftime("%Y-%m-%d")
        daily_data[date_str][status] = count
        
    # Sort and keep the last 14 dates
    sorted_dates = sorted(daily_data.keys())[-14:]
    attendance_dates = sorted_dates
    eating_counts = [daily_data[d]['eating'] for d in sorted_dates]
    skipping_counts = [daily_data[d]['skipping'] for d in sorted_dates]

    # 5. Food wastage trends (last 14 records)
    waste_records = FoodWasteRecord.query.order_by(FoodWasteRecord.date.asc()).all()
    # Summarize duplicate dates by summing prepared/wasted
    waste_daily = defaultdict(lambda: {'prepared': 0.0, 'wasted': 0.0})
    for wr in waste_records:
        d_str = wr.date.strftime("%Y-%m-%d")
        waste_daily[d_str]['prepared'] += wr.food_prepared
        waste_daily[d_str]['wasted'] += wr.food_wasted
        
    sorted_waste_dates = sorted(waste_daily.keys())[-14:]
    waste_dates = sorted_waste_dates
    prepared_trends = [round(waste_daily[d]['prepared'], 2) for d in sorted_waste_dates]
    wasted_trends = [round(waste_daily[d]['wasted'], 2) for d in sorted_waste_dates]

    # 6. Attendance grouped by meal type (total aggregate historical bookings)
    meal_agg_query = db.session.query(
        MealBooking.meal_type,
        MealBooking.status,
        func.count(MealBooking.id)
    ).group_by(MealBooking.meal_type, MealBooking.status).all()
    
    meal_agg = {
        'breakfast': {'eating': 0, 'skipping': 0},
        'lunch': {'eating': 0, 'skipping': 0},
        'dinner': {'eating': 0, 'skipping': 0}
    }
    for meal, status, count in meal_agg_query:
        if meal in meal_agg and status in ['eating', 'skipping']:
            meal_agg[meal][status] = count

    return {
        'avg_ratings': avg_ratings,
        'avg_waste_pct': avg_waste_pct,
        'most_skipped_meal': most_skipped_meal.capitalize(),
        'attendance_dates': attendance_dates,
        'eating_counts': eating_counts,
        'skipping_counts': skipping_counts,
        'waste_dates': waste_dates,
        'prepared_trends': prepared_trends,
        'wasted_trends': wasted_trends,
        'meal_agg': meal_agg
    }
