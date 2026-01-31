# Parking Slot Reservation Application

A minimal, production-ready Flask monolithic application for parking slot reservations with Docker support.

## Features

✨ **Core Functionality**
- User authentication (register, login, logout)
- View available parking slots in real-time
- Reserve parking slots with one click
- Generate QR codes for reservations
- View reservation history
- Secure session-based authentication

🏗️ **Architecture**
- Monolithic Flask application
- SQLAlchemy ORM with SQLite database
- Flask-Login for authentication
- Jinja2 templates for rendering
- Responsive CSS (no frameworks)
- QR code generation with `qrcode` library

🐳 **Docker Support**
- Multi-stage Docker build for optimized images
- Docker Compose for local development
- Health checks included
- Volume mounting for live code reloading

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### 2. Setup

```bash
# Clone/navigate to project directory
cd parking_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

**Access the app**: http://localhost:5000

### 3. First Time Setup

The database and parking slots are automatically created on first run. You'll see 10 parking slots (A-01 through A-10) ready to reserve.

---

## Quick Start (Docker)

### 1. Prerequisites
- Docker
- Docker Compose

### 2. Run with Docker Compose

```bash
# Build and start the application
docker-compose up --build

# Access the app: http://localhost:5000
```

**Live Reloading**: Changes to `.py` files and templates are reflected immediately thanks to volume mounting.

### 3. Stop the Application

```bash
docker-compose down
```

### 4. Build Docker Image Only

```bash
# Build the production image
docker build -t parking-app:latest .

# Run the container
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -v $(pwd)/instance:/app/instance \
  parking-app:latest
```

---

## 🌐 Quick Tunnel with Cloudflare (Public Access)

### Share Your Local App Instantly

Expose your locally-running Flask app to the internet without deploying:

```bash
# Prerequisites: Install cloudflared
# Download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

# Start your Flask app first
python app.py

# In a new terminal, run cloudflare tunnel
cloudflared tunnel --url http://localhost:5000
```

**Output**: You'll get a unique public URL:
```
https://your-unique-id.trycloudflare.com
```

**Use Cases**:
- ✅ Share app with team/clients for testing
- ✅ Demo features without deployment
- ✅ Quick feedback iterations
- ✅ Test from mobile devices
- ✅ Staging before production deployment

**Limitations**:
- Tunnel only active while `cloudflared` is running
- URL changes each time you restart
- No authentication by default
- For persistent URLs, create a paid Cloudflare tunnel

---

## Project Structure

```
parking_app/
├── app.py                          # Flask app factory & configuration
├── models.py                       # SQLAlchemy data models
├── auth.py                         # Authentication routes & logic
├── routes.py                       # Slot & reservation routes
├── utils.py                        # QR generation & validators
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker Compose config
├── .dockerignore                   # Files to exclude from Docker build
│
├── templates/
│   ├── base.html                   # Base template with navigation
│   ├── index.html                  # Home/landing page
│   ├── login.html                  # Login form
│   ├── register.html               # Registration form
│   ├── slots.html                  # List available slots
│   ├── reservation_create.html     # Reservation confirmation
│   ├── reservation_success.html    # Success page with QR code
│   ├── my_reservations.html        # User's reservation history
│   └── error.html                  # Error page template
│
├── static/
│   └── style.css                   # Minimal responsive CSS
│
├── instance/
│   └── parking.db                  # SQLite database (auto-created)
│
├── DESIGN.md                       # Architecture & design documentation
└── README.md                       # This file
```

---

## User Journey Example

### 1. Register
```
User → Visit http://localhost:5000
     → Click "Register"
     → Enter email: john@example.com
     → Enter password: secure123
     → Confirm password
     → Account created, redirect to login
```

### 2. Login
```
User → Enter email: john@example.com
     → Enter password: secure123
     → Authenticated, session created
     → Redirect to /slots
```

### 3. View Slots
```
User → See all 10 parking slots (A-01 to A-10)
     → Slots marked as "Available" or "Reserved"
     → Click "Reserve Now" on available slot
```

### 4. Reserve Slot
```
User → Click "Reserve Now" on Slot A-03
     → Confirm reservation
     → Slot marked as unavailable
     → Redirect to confirmation page with QR code
```

### 5. View QR Code
```
QR Code payload (JSON):
{
  "reservation_id": 1,
  "user_email": "john@example.com",
  "slot_number": "A-03",
  "reserved_at": "2026-01-31T14:30:00",
  "app_version": "1.0"
}
```

---

## Technology Stack

| Technology | Purpose | Version |
|---|---|---|
| Python | Runtime | 3.10+ |
| Flask | Web framework | 2.3.2 |
| SQLAlchemy | ORM | 3.0.5 |
| SQLite | Database | Built-in |
| Flask-Login | Authentication | 0.6.2 |
| qrcode | QR generation | 7.4.2 |
| Pillow | Image processing | 10.0.0 |
| Docker | Containerization | Latest |

---

## API Routes

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home page |
| GET | `/auth/register` | Registration form |
| POST | `/auth/register` | Create user account |
| GET | `/auth/login` | Login form |
| POST | `/auth/login` | Authenticate user |
| GET | `/auth/logout` | Logout & clear session |

### Parking Slots
| Method | Endpoint | Description |
|---|---|---|
| GET | `/slots/` | List all slots |
| GET | `/slots/available` | List available slots only |

### Reservations
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/reservations/create?slot_id=3` | Reservation form | Yes |
| POST | `/reservations/create` | Create reservation | Yes |
| GET | `/reservations/<id>` | View reservation + QR | Yes |
| GET | `/reservations/` | User's reservations | Yes |

---

## Configuration

### Environment Variables

```bash
# Flask app factory
FLASK_APP=app.py
FLASK_ENV=production          # or development

# Security
SECRET_KEY=your-secret-key    # Change in production!

# Database
DATABASE_URL=sqlite:///parking.db

# Session
SESSION_COOKIE_SECURE=False   # Set to True in production (HTTPS)
SESSION_COOKIE_HTTPONLY=True  # Prevent JS access to cookies
SESSION_COOKIE_SAMESITE=Lax   # CSRF protection
```

### Docker Environment

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - FLASK_ENV=development
  - SECRET_KEY=your-secret-key
  - DATABASE_URL=sqlite:///parking.db
```

---

## Database Schema

### User Table
```
id (PK), email (UNIQUE), password_hash, created_at
```

### ParkingSlot Table
```
id (PK), slot_number (UNIQUE), is_available, created_at
```

### Reservation Table
```
id (PK), user_id (FK), slot_id (FK), reserved_at, qr_code_data
```

---

## Security Features

✅ Password hashing with Werkzeug PBKDF2  
✅ Session-based authentication with Flask-Login  
✅ CSRF protection via WTForms  
✅ Secure cookies (HttpOnly, SameSite)  
✅ SQL injection prevention (SQLAlchemy ORM)  
✅ Double-booking prevention (DB constraints + app logic)  
✅ User authorization checks on protected routes  
✅ Input validation on all forms  

---

## Production Deployment

### 1. Generate a Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Set Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY=your-generated-secret-key
export SESSION_COOKIE_SECURE=True
export SESSION_COOKIE_SAMESITE=Strict
```

### 3. Use a Production WSGI Server

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Docker Production Build

```bash
docker build -t parking-app:v1.0 .
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e FLASK_ENV=production \
  -v parking_db:/app/instance \
  --name parking-prod \
  parking-app:v1.0
```

### 5. Migrate Database (PostgreSQL)

```bash
# Update DATABASE_URL
export DATABASE_URL=postgresql://user:password@localhost:5432/parking_db

# Run migrations with Alembic (future enhancement)
```

---

## Testing

### Manual Testing

```bash
# Test registration
curl -X POST http://localhost:5000/auth/register \
  -d "email=test@example.com&password=password123&password_confirm=password123"

# Test login
curl -X POST http://localhost:5000/auth/login \
  -d "email=test@example.com&password=password123" \
  -c cookies.txt

# Test slots
curl http://localhost:5000/slots/ -b cookies.txt
```

### Automated Testing (Future)

```bash
pip install pytest pytest-flask
pytest tests/
```

---

## Troubleshooting

### Issue: `"ModuleNotFoundError: No module named 'flask'"`

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Issue: `"Database is locked"`

**Solution**: SQLite can have locking issues with multiple processes. Use PostgreSQL for production or ensure only one process accesses the DB.

### Issue: `"Port 5000 already in use"`

**Solution**: Use a different port:
```bash
python -c "from app import app; app.run(port=5001)"
# Or with Docker
docker-compose down && docker-compose up
```

### Issue: QR code not generating

**Solution**: Ensure Pillow is installed:
```bash
pip install --upgrade Pillow
```

---

## Future Enhancements

- 🔄 Database migrations with Alembic
- 📊 Admin dashboard for slot management
- 📧 Email notifications for reservations
- ⏰ Reservation expiration & cancellation
- 📱 Mobile app (React Native)
- 🗺️ Interactive parking lot map
- 🔐 2FA authentication
- 📝 Audit logging
- 🚀 Multi-location support

---

## License

MIT License - Feel free to use and modify

---

## Support

For issues or questions:
1. Check [DESIGN.md](DESIGN.md) for architecture details
2. Review code comments in source files
3. Test with `docker-compose up` for isolated environment

---

## Contributing

Contributions are welcome! Please follow:
- PEP 8 code style
- Add tests for new features
- Update documentation

---

**Happy Parking! 🅿️**
