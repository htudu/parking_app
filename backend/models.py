from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db


class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class ParkingSlot(db.Model):
    """Parking slot model"""
    id = db.Column(db.Integer, primary_key=True)
    slot_number = db.Column(db.String(10), unique=True, nullable=False, index=True)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='slot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingSlot {self.slot_number}>'


class Reservation(db.Model):
    """Reservation model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slot.id'), nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_data = db.Column(db.Text)  # JSON string with QR payload
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id} - Slot {self.slot_id}>'
