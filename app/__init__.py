import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.models import db, User
from config import Config

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError("SECRET_KEY environment variable is required. Set it in your shell or .env file before starting the app.")
    
    # Bind extensions to app lifecycle
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register Blueprints
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.admin.routes import admin_bp
    from app.analytics.routes import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # Main/Home routes (Landing page)
    @app.route('/')
    def home():
        return render_template('home.html')
        
    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
        
    # Database Initialization CLI Command
    @app.cli.command('init-db')
    def init_db_command():
        """Clear the existing data and create new tables."""
        db.create_all()
        app.logger.info("Database initialized successfully.")
        print("Database initialized successfully.")
        
    return app
