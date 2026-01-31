import os
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for
from flask_login import current_user
from backend.extensions import db, login_manager


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///parking.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create app context for initialization
    with app.app_context():
        # Import models
        from backend.models import User, ParkingSlot, Reservation
        
        # Create tables
        db.create_all()
        
        # Seed parking slots if empty
        if ParkingSlot.query.count() == 0:
            for i in range(1, 11):
                slot = ParkingSlot(slot_number=f"A-{i:02d}")
                db.session.add(slot)
            db.session.commit()
        
        # User loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    # Register blueprints
    from backend.auth import auth_bp
    from backend.routes import slots_bp, reservations_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(slots_bp)
    app.register_blueprint(reservations_bp)
    
    # Root route handler
    @app.route('/')
    def root():
        """Root route - redirect to appropriate page based on auth status"""
        if current_user.is_authenticated:
            return redirect(url_for('slots.list_slots'))
        else:
            return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('error.html', message='Page not found', code=404), 404
    
    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('error.html', message='Server error', code=500), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
