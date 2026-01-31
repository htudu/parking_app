import json
import base64
from io import BytesIO
from datetime import datetime
import qrcode


def validate_email(email):
    """Basic email validation"""
    if not email or '@' not in email or '.' not in email.split('@')[1]:
        raise ValueError('Invalid email format')
    return True


def validate_password(password):
    """Validate password strength"""
    if not password:
        raise ValueError('Password is required')
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    return True


def generate_qr_code(reservation_id, user_email, slot_number, timestamp):
    """
    Generate QR code as base64 PNG image
    
    Args:
        reservation_id: Reservation ID
        user_email: User email
        slot_number: Parking slot number
        timestamp: Reservation timestamp
    
    Returns:
        Base64 encoded PNG image data URI
    """
    payload = {
        "reservation_id": reservation_id,
        "user_email": user_email,
        "slot_number": slot_number,
        "reserved_at": timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp),
        "app_version": "1.0"
    }
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Return as data URI
    return f"data:image/png;base64,{img_base64}", json.dumps(payload)


def get_reservation_summary(reservation):
    """Get formatted reservation summary"""
    return {
        'id': reservation.id,
        'user_email': reservation.user.email,
        'slot_number': reservation.slot.slot_number,
        'reserved_at': reservation.reserved_at.strftime('%Y-%m-%d %H:%M:%S'),
        'qr_code_payload': json.loads(reservation.qr_code_data) if reservation.qr_code_data else None
    }
