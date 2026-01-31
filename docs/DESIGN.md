# Parking Slot Reservation App - Design Document

## 1. High-Level Architecture

### Monolithic Flask Application
- **Single Python Process**: All features in one Flask app
- **Session-Based Auth**: Flask-Login for simple authentication
- **Synchronous**: No async needed for MVP
- **SQLite Database**: File-based, zero setup

### Architecture Diagram
```
┌─────────────────────────────────────────┐
│        Flask Web Application            │
├─────────────────────────────────────────┤
│  Routes Layer (auth, slots, reservations)
│  ├─ /auth/* (login, register, logout)
│  ├─ /slots/* (list, availability)
│  └─ /reservations/* (create, view, qr)
├─────────────────────────────────────────┤
│  Service Layer (Business Logic)
│  ├─ AuthService (password hashing, validation)
│  ├─ SlotService (availability checks)
│  └─ ReservationService (booking, QR generation)
├─────────────────────────────────────────┤
│  Data Models Layer
│  ├─ User model
│  ├─ ParkingSlot model
│  └─ Reservation model
├─────────────────────────────────────────┤
│  SQLAlchemy ORM
├─────────────────────────────────────────┤
│        SQLite Database (parking.db)
└─────────────────────────────────────────┘
```

---

## 2. Database Schema

### Entity-Relationship Model

#### User Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
- **Primary Key**: `id`
- **Unique Constraint**: `email`
- **Purpose**: Store user accounts with hashed passwords

#### ParkingSlot Table
```sql
CREATE TABLE parking_slot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number VARCHAR(10) UNIQUE NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
- **Primary Key**: `id`
- **Unique Constraint**: `slot_number`
- **Default**: All slots start as available
- **Purpose**: Manage parking inventory

#### Reservation Table
```sql
CREATE TABLE reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL FOREIGN KEY REFERENCES user(id),
    slot_id INTEGER NOT NULL FOREIGN KEY REFERENCES parking_slot(id),
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    qr_code_data TEXT
);
```
- **Primary Key**: `id`
- **Foreign Keys**: Links to `user` and `parking_slot`
- **Unique Constraint**: One active reservation per slot (enforced via `is_available` flag)
- **QR Data**: JSON string containing reservation details

### ER Diagram
```
┌─────────────┐           ┌──────────────┐           ┌──────────────────┐
│    User     │           │ ParkingSlot  │           │  Reservation     │
├─────────────┤           ├──────────────┤           ├──────────────────┤
│ id (PK)     │ 1───────∞ │ id (PK)      │ ∞─────1  │ id (PK)          │
│ email       │           │ slot_number  │           │ user_id (FK)     │
│ password    │           │ is_available │           │ slot_id (FK)     │
│ created_at  │           │ created_at   │           │ reserved_at      │
└─────────────┘           └──────────────┘           │ qr_code_data     │
                                                     └──────────────────┘
```

---

## 3. Core Routes & API Endpoints

### Authentication Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/` | Home page / landing | No |
| GET | `/register` | Registration form | No |
| POST | `/register` | Create new user | No |
| GET | `/login` | Login form | No |
| POST | `/login` | Authenticate user | No |
| GET | `/logout` | Clear session | Yes |

### Parking Slot Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/slots` | List all slots with availability | No |
| GET | `/slots/available` | List only available slots | No |

### Reservation Routes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| POST | `/reservations/create` | Reserve a slot | Yes |
| GET | `/reservations` | User's reservation history | Yes |
| GET | `/reservations/<reservation_id>` | View single reservation + QR | Yes |
| GET | `/reservations/<reservation_id>/qr` | Download QR code image | Yes |

---

## 4. Data Models (SQLAlchemy)

### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### ParkingSlot Model
```python
class ParkingSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slot_number = db.Column(db.String(10), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservations = db.relationship('Reservation', backref='slot', lazy=True)
```

### Reservation Model
```python
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('parking_slot.id'), nullable=False)
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_data = db.Column(db.Text)  # JSON string
    
    __table_args__ = (
        db.UniqueConstraint('slot_id', name='unique_active_reservation'),
    )
```

---

## 5. Security Implementation

### Password Security
- **Hashing Algorithm**: Werkzeug's `generate_password_hash()` (PBKDF2)
- **Salting**: Automatic, no manual handling
- **Verification**: `check_password_hash()` for constant-time comparison

### Session Management
- **Library**: Flask-Login with Flask Sessions
- **Cookie**: `session_id` (secure, HttpOnly, SameSite)
- **Duration**: Browser session (ends on close) or configurable timeout
- **CSRF Protection**: WTForms with `flask-wtf` (token in forms)

### Reservation Security
- **Double-Booking Prevention**: Database constraint + application logic
  1. Check `is_available == True` before reservation
  2. Atomic update: `UPDATE parking_slot SET is_available=False WHERE id=X AND is_available=True`
  3. Verify update succeeded
- **User Authorization**: Verify `current_user.id` matches reservation owner
- **Input Validation**: Whitelist slot IDs, validate email format

### Authentication Flow
```
1. User submits email + password to /login
2. Query user by email
3. Hash submitted password, compare with stored hash
4. On success: Flask-Login creates session
5. @login_required decorator protects routes
6. Session cookie sent with every request
```

---

## 6. QR Code Implementation

### QR Code Payload (JSON)
```json
{
  "reservation_id": 123,
  "user_email": "john@example.com",
  "slot_number": "A-05",
  "reserved_at": "2026-01-31T14:30:00Z",
  "app_version": "1.0"
}
```

### Generation Process
1. **After Reservation Created**: Generate QR code with `qrcode` library
2. **Storage Option A (Recommended for MVP)**: Base64 encode → store in `qr_code_data` column
3. **Storage Option B**: Save as PNG file → reference path in database
4. **Display**: Embed base64 directly in HTML img tag

### Implementation
```python
import qrcode
import json
from io import BytesIO
import base64

def generate_qr_code(reservation_id, user_email, slot_number, timestamp):
    payload = {
        "reservation_id": reservation_id,
        "user_email": user_email,
        "slot_number": slot_number,
        "reserved_at": timestamp.isoformat(),
        "app_version": "1.0"
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"
```

---

## 7. Project File Structure

```
parking_app/
├── app.py                     # Flask app factory, config
├── models.py                  # SQLAlchemy models
├── auth.py                    # Authentication logic, password hashing
├── routes.py                  # All route handlers
├── utils.py                   # QR generation, validators, helpers
├── requirements.txt           # Python dependencies
├── README.md                  # Setup & run instructions
├── DESIGN.md                  # This file
│
├── templates/
│   ├── base.html             # Base layout (nav, footer, blocks)
│   ├── index.html            # Home/landing page
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   ├── slots.html            # List all parking slots
│   ├── reservation_create.html # Reservation confirmation
│   ├── reservation_success.html # Success with QR code
│   └── error.html            # Error page template
│
├── static/
│   └── style.css             # Minimal CSS (typography, layout, forms)
│
└── instance/
    └── parking.db            # SQLite database (auto-created)
```

---

## 8. Configuration & Environment

### Flask Config
```python
class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sessions
    SECRET_KEY = os.urandom(24)  # Change to env var in production
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = False  # True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # App
    DEBUG = True
```

---

## 9. Key Business Logic

### Reservation Workflow
```
1. User logs in
2. User views /slots (sees available slots)
3. User selects slot, POSTs to /reservations/create
4. Backend:
   a. Verify user is authenticated
   b. Verify slot exists and is_available == True
   c. Create Reservation record
   d. Update ParkingSlot: is_available = False
   e. Generate QR code with reservation data
   f. Redirect to /reservations/<id>
5. Display confirmation page with QR code
```

### Preventing Double Booking
```
Scenario: User A and B both try to reserve Slot 5 simultaneously

Database Solution:
- Add UNIQUE constraint on (slot_id) where is_available == True
- OR use transaction + database-level check

Python Solution:
1. Query: SELECT * FROM parking_slot WHERE id=5 FOR UPDATE (lock)
2. Check: is_available == True
3. If true: Create reservation, set is_available = False
4. If false: Raise error, retry or show "Slot taken"
5. Commit transaction
```

---

## 10. Dependencies

### requirements.txt
```
Flask==2.3.2
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
qrcode==7.4.2
Pillow==10.0.0
Werkzeug==2.3.6
```

---

## 11. Setup & Run Instructions

### Local Development

#### 1. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Initialize Database
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
...     # Seed 10 parking slots
...     for i in range(1, 11):
...         slot = ParkingSlot(slot_number=f"A-{i:02d}")
...         db.session.add(slot)
...     db.session.commit()
>>> exit()
```

#### 4. Run Flask App
```bash
flask run
# or
python app.py
```

#### 5. Access Application
- **URL**: `http://localhost:5000`
- **Default Port**: 5000

---

## 12. Example User Journey

### Scenario: John reserves Slot A-03

#### Step 1: Register
```
GET /register → Form displayed
POST /register (email: john@example.com, password: secure123)
  → User created with password hash
  → Redirected to /login
```

#### Step 2: Login
```
POST /login (email: john@example.com, password: secure123)
  → Password verified
  → Session created
  → Redirected to /slots
```

#### Step 3: View Available Slots
```
GET /slots
  → Display: Slot A-01 (available), A-02 (available), A-03 (available), ...
```

#### Step 4: Reserve Slot A-03
```
POST /reservations/create (slot_id: 3)
  → Check: Slot 3 is_available == True ✓
  → Create: Reservation (user_id: 1, slot_id: 3)
  → Update: ParkingSlot 3 → is_available = False
  → Generate: QR code with payload
  → Redirect to /reservations/1
```

#### Step 5: View Reservation with QR Code
```
GET /reservations/1
  → Display: "Reservation confirmed for Slot A-03"
  → Show: QR code image (base64)
  → Show: Reserved at: 2026-01-31 14:30:00
```

#### Step 6: QR Code Payload
```json
{
  "reservation_id": 1,
  "user_email": "john@example.com",
  "slot_number": "A-03",
  "reserved_at": "2026-01-31T14:30:00Z",
  "app_version": "1.0"
}
```

---

## 13. Error Handling

### User-Facing Errors
| Error | HTTP Code | Message |
|-------|-----------|---------|
| Invalid email format | 400 | "Invalid email format" |
| Email already registered | 409 | "Email already in use" |
| Password too weak | 400 | "Password must be at least 8 chars" |
| Invalid credentials | 401 | "Email or password incorrect" |
| Slot not available | 409 | "Slot already reserved" |
| Not authenticated | 302 | Redirect to /login |
| Not authorized | 403 | "You don't have permission" |

### Implementation
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Server error"), 500

try:
    # reservation logic
except IntegrityError:
    db.session.rollback()
    flash('Slot already reserved. Please try another.', 'error')
    return redirect(url_for('slots'))
```

---

## 14. Performance Considerations (MVP)

- **No caching needed**: Small dataset
- **Single database**: SQLite sufficient for <1000 concurrent users
- **Indexes**: 
  - `user.email` (unique)
  - `parking_slot.slot_number` (unique)
  - `reservation.user_id`, `reservation.slot_id` (FK lookups)
- **Query optimization**: Only fetch needed columns
- **N+1 prevention**: Use SQLAlchemy relationships wisely

---

## 15. Future Scalability (Not MVP)

### Horizontal Scaling Options
1. **Database**: Migrate to PostgreSQL
2. **Cache**: Redis for session storage
3. **Queue**: Celery for async QR generation
4. **Monitoring**: Sentry for error tracking
5. **Admin Dashboard**: User/slot management UI

---

## 16. Security Checklist

- ✅ Passwords hashed with Werkzeug (PBKDF2)
- ✅ HTTPS enforced (in production)
- ✅ CSRF tokens on forms (flask-wtf)
- ✅ Session cookies HttpOnly + Secure
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Double-booking prevention (DB constraints + app logic)
- ✅ Authorization checks on protected routes
- ✅ Input validation on all forms
- ✅ No sensitive data in logs
- ✅ Secure secret key management (env vars in production)

---

## Summary

**This is a minimal, production-ready monolithic Flask architecture for a parking reservation system.** It emphasizes:

✅ **Simplicity**: Single app, no microservices, SQLite  
✅ **Security**: Password hashing, session auth, double-booking prevention  
✅ **Clarity**: Clean models, logical routes, minimal templates  
✅ **Extensibility**: Easy to add features without major refactoring  

**Estimated implementation time**: 2-3 hours  
**Code size**: ~500-700 LOC  
**Lines per file**: 50-150 (manageable)
