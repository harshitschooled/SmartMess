import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app.models import db, User, MealBooking, Menu, FoodWasteRecord, Feedback
from flask import Blueprint
admin_bp = Blueprint('admin', __name__)
from app.auth.routes import admin_required
from app.admin.forms import MenuForm, FoodWasteForm
from app.services import booking_service

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    today = booking_service.get_current_time().date()
    
    # Registered students count
    students_count = User.query.filter_by(role='student').count()
    
    # Expected attendance (Eating) for today
    expected_breakfast = MealBooking.query.filter_by(date=today, meal_type='breakfast', status='eating').count()
    expected_lunch = MealBooking.query.filter_by(date=today, meal_type='lunch', status='eating').count()
    expected_dinner = MealBooking.query.filter_by(date=today, meal_type='dinner', status='eating').count()
    
    # Skipping counts for today
    skipping_breakfast = MealBooking.query.filter_by(date=today, meal_type='breakfast', status='skipping').count()
    skipping_lunch = MealBooking.query.filter_by(date=today, meal_type='lunch', status='skipping').count()
    skipping_dinner = MealBooking.query.filter_by(date=today, meal_type='dinner', status='skipping').count()
    
    # Recent food waste records (past 5 records)
    recent_waste = FoodWasteRecord.query.order_by(FoodWasteRecord.date.desc()).limit(5).all()
    
    # Recent feedback records (past 5 records)
    recent_feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        today=today,
        students_count=students_count,
        expected_breakfast=expected_breakfast,
        expected_lunch=expected_lunch,
        expected_dinner=expected_dinner,
        skipping_breakfast=skipping_breakfast,
        skipping_lunch=skipping_lunch,
        skipping_dinner=skipping_dinner,
        recent_waste=recent_waste,
        recent_feedback=recent_feedback
    )


@admin_bp.route('/menus')
@login_required
@admin_required
def manage_menus():
    # Filter by date, default is today and the next 7 days
    date_str = request.args.get('date')
    if date_str:
        try:
            filter_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            menus = Menu.query.filter_by(date=filter_date).order_by(Menu.meal_type).all()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('admin.manage_menus'))
    else:
        today = booking_service.get_current_time().date()
        menus = Menu.query.filter(Menu.date >= today).order_by(Menu.date.asc(), Menu.meal_type.asc()).all()
        
    return render_template('admin/menus.html', menus=menus, selected_date=date_str)


@admin_bp.route('/menu/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_menu():
    form = MenuForm()
    
    # Prefill date from query parameters if available
    if request.method == 'GET' and request.args.get('date'):
        try:
            form.date.data = datetime.datetime.strptime(request.args.get('date'), "%Y-%m-%d").date()
        except ValueError:
            pass
            
    if form.validate_on_submit():
        # Check uniqueness constraint: one menu record per date and meal type
        existing_menu = Menu.query.filter_by(date=form.date.data, meal_type=form.meal_type.data).first()
        if existing_menu:
            flash(f'A menu for {form.date.data} - {form.meal_type.data.capitalize()} already exists. Please edit that record instead.', 'warning')
            return render_template('admin/menu_form.html', form=form, title="Create Menu")
            
        menu = Menu(
            date=form.date.data,
            meal_type=form.meal_type.data,
            items=form.items.data.strip()
        )
        db.session.add(menu)
        db.session.commit()
        flash('Menu created successfully!', 'success')
        return redirect(url_for('admin.manage_menus'))
        
    return render_template('admin/menu_form.html', form=form, title="Create Menu")


@admin_bp.route('/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    form = MenuForm(obj=menu)
    
    if form.validate_on_submit():
        # Check uniqueness when editing (if date or type changed)
        existing_menu = Menu.query.filter(
            Menu.date == form.date.data,
            Menu.meal_type == form.meal_type.data,
            Menu.id != menu.id
        ).first()
        
        if existing_menu:
            flash(f'A menu for {form.date.data} - {form.meal_type.data.capitalize()} already exists.', 'warning')
            return render_template('admin/menu_form.html', form=form, title="Edit Menu")
            
        menu.date = form.date.data
        menu.meal_type = form.meal_type.data
        menu.items = form.items.data.strip()
        db.session.commit()
        
        flash('Menu updated successfully!', 'success')
        return redirect(url_for('admin.manage_menus'))
        
    return render_template('admin/menu_form.html', form=form, title="Edit Menu", menu=menu)


@admin_bp.route('/menu/delete/<int:menu_id>', methods=['POST'])
@login_required
@admin_required
def delete_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu deleted successfully.', 'success')
    return redirect(url_for('admin.manage_menus'))


@admin_bp.route('/waste')
@login_required
@admin_required
def food_waste():
    records = FoodWasteRecord.query.order_by(FoodWasteRecord.date.desc(), FoodWasteRecord.meal_type.desc()).all()
    return render_template('admin/food_waste.html', records=records)


@admin_bp.route('/waste/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_waste():
    form = FoodWasteForm()
    
    # Prefill date from query params if available
    if request.method == 'GET' and request.args.get('date'):
        try:
            form.date.data = datetime.datetime.strptime(request.args.get('date'), "%Y-%m-%d").date()
        except ValueError:
            pass

    if form.validate_on_submit():
        existing_record = FoodWasteRecord.query.filter_by(
            date=form.date.data,
            meal_type=form.meal_type.data
        ).first()
        if existing_record:
            flash(f'A food waste record for {form.date.data} - {form.meal_type.data.capitalize()} already exists. Please edit that record instead.', 'warning')
            return render_template('admin/food_waste_form.html', form=form, title="Log Food Waste")
            
        # Calculate expected students count from meal bookings
        expected_count = MealBooking.query.filter_by(
            date=form.date.data,
            meal_type=form.meal_type.data,
            status='eating'
        ).count()
        
        prepared = float(form.food_prepared.data)
        consumed = float(form.food_consumed.data)
        wasted = prepared - consumed
        
        record = FoodWasteRecord(
            date=form.date.data,
            meal_type=form.meal_type.data,
            expected_students=expected_count,
            food_prepared=prepared,
            food_consumed=consumed,
            food_wasted=wasted
        )
        db.session.add(record)
        db.session.commit()
        flash('Food waste record logged successfully!', 'success')
        return redirect(url_for('admin.food_waste'))
        
    return render_template('admin/food_waste_form.html', form=form, title="Log Food Waste")


@admin_bp.route('/waste/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_waste(record_id):
    record = FoodWasteRecord.query.get_or_404(record_id)
    form = FoodWasteForm(obj=record)
    
    if form.validate_on_submit():
        existing_record = FoodWasteRecord.query.filter(
            FoodWasteRecord.date == form.date.data,
            FoodWasteRecord.meal_type == form.meal_type.data,
            FoodWasteRecord.id != record.id
        ).first()
        if existing_record:
            flash(f'A food waste record for {form.date.data} - {form.meal_type.data.capitalize()} already exists.', 'warning')
            return render_template('admin/food_waste_form.html', form=form, title="Edit Waste Record")
            
        # Recalculate expected students count from meal bookings
        expected_count = MealBooking.query.filter_by(
            date=form.date.data,
            meal_type=form.meal_type.data,
            status='eating'
        ).count()
        
        prepared = float(form.food_prepared.data)
        consumed = float(form.food_consumed.data)
        wasted = prepared - consumed
        
        record.date = form.date.data
        record.meal_type = form.meal_type.data
        record.expected_students = expected_count
        record.food_prepared = prepared
        record.food_consumed = consumed
        record.food_wasted = wasted
        
        db.session.commit()
        flash('Food waste record updated successfully!', 'success')
        return redirect(url_for('admin.food_waste'))
        
    return render_template('admin/food_waste_form.html', form=form, title="Edit Waste Record", record=record)


@admin_bp.route('/waste/delete/<int:record_id>', methods=['POST'])
@login_required
@admin_required
def delete_waste(record_id):
    record = FoodWasteRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Food waste record deleted successfully.', 'success')
    return redirect(url_for('admin.food_waste'))


@admin_bp.route('/feedback')
@login_required
@admin_required
def view_feedback():
    feedbacks = Feedback.query.order_by(Feedback.date.desc(), Feedback.created_at.desc()).all()
    
    # Calculate average ratings by meal type
    avg_breakfast = db.session.query(db.func.avg(Feedback.rating)).filter_by(meal_type='breakfast').scalar() or 0.0
    avg_lunch = db.session.query(db.func.avg(Feedback.rating)).filter_by(meal_type='lunch').scalar() or 0.0
    avg_dinner = db.session.query(db.func.avg(Feedback.rating)).filter_by(meal_type='dinner').scalar() or 0.0
    
    return render_template(
        'admin/feedback.html',
        feedbacks=feedbacks,
        avg_breakfast=round(avg_breakfast, 2),
        avg_lunch=round(avg_lunch, 2),
        avg_dinner=round(avg_dinner, 2)
    )
