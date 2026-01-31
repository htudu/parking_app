from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from backend.extensions import db
from backend.models import User
from backend.utils import validate_email, validate_password


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/')
@login_required
def index():
    """Home page - requires login"""
    return render_template('index.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('slots.list_slots'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validation
        try:
            validate_email(email)
            validate_password(password)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('auth.register'))
        
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('auth.login'))
        
        try:
            # Create user
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('slots.list_slots'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome, {user.email}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('slots.list_slots'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout - requires login"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.index'))
