import io
from flask import render_template, Response, redirect, url_for, flash
from flask_login import login_required
from flask import Blueprint
analytics_bp = Blueprint('analytics', __name__)
from app.auth.routes import admin_required
from app.services import analytics_service, report_service

@analytics_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    data = analytics_service.get_analytics_data()
    return render_template('analytics/dashboard.html', data=data)


@analytics_bp.route('/export/bookings')
@login_required
@admin_required
def export_bookings():
    output = io.StringIO()
    report_service.generate_bookings_csv(output)
    csv_data = output.getvalue()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=bookings_report.csv"}
    )


@analytics_bp.route('/export/waste')
@login_required
@admin_required
def export_waste():
    output = io.StringIO()
    report_service.generate_waste_csv(output)
    csv_data = output.getvalue()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=food_waste_report.csv"}
    )


@analytics_bp.route('/export/feedback')
@login_required
@admin_required
def export_feedback():
    output = io.StringIO()
    report_service.generate_feedback_csv(output)
    csv_data = output.getvalue()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=feedback_report.csv"}
    )
