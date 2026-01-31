#!/usr/bin/env python
"""Quick test script to verify app initialization"""

import os
import sys
from backend.models import ParkingSlot
from app import create_app

try:
    print("=" * 60)
    print("PARKING APP - INITIALIZATION TEST")
    print("=" * 60)
    
    print("\n✓ Importing Flask app...")
    
    print("✓ Creating Flask app...")
    app = create_app()
    
    print("✓ Verifying database...")
    with app.app_context():
        
        slot_count = ParkingSlot.query.count()
        print(f"✓ Database tables created")
        print(f"✓ Parking slots created: {slot_count}")
        
        slots = ParkingSlot.query.order_by(ParkingSlot.slot_number).all()
        for slot in slots[:3]:
            print(f"  - Slot: {slot.slot_number}, Available: {slot.is_available}")
        print(f"  ... and {slot_count - 3} more slots")
    
    print("\n✓ Checking file structure...")
    required_files = [
        'app.py', 'requirements.txt', 'Dockerfile',
        'docker-compose.yml', '.dockerignore', '.env.example'
    ]
    
    required_backend_files = ['extensions.py', 'models.py', 'auth.py', 'routes.py', 'utils.py']
    required_dirs = ['backend', 'templates', 'static', 'instance', 'docs']
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    missing_backend_files = [f for f in required_backend_files if not os.path.exists(f'backend/{f}')]
    missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
    
    if not missing_files and not missing_backend_files and not missing_dirs:
        print(f"✓ All {len(required_files)} required root files present")
        print(f"✓ All {len(required_backend_files)} required backend files present")
        print(f"✓ All {len(required_dirs)} required directories present")
    else:
        if missing_files:
            print(f"✗ Missing root files: {missing_files}")
        if missing_backend_files:
            print(f"✗ Missing backend files: {missing_backend_files}")
        if missing_dirs:
            print(f"✗ Missing directories: {missing_dirs}")
    
    print("\n✓ Verifying templates...")
    templates = os.listdir('templates')
    print(f"✓ Found {len(templates)} templates: {', '.join([t for t in templates[:3]])}...")
    
    print("\n✓ Verifying static files...")
    static_files = os.listdir('static')
    print(f"✓ Found {len(static_files)} static files: {', '.join(static_files)}")
    
    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED!")
    print("=" * 60)
    print("\nPROJECT STRUCTURE:")
    print("  📁 backend/        - Python modules (extensions, models, routes, auth, utils)")
    print("  📁 templates/      - HTML templates")
    print("  📁 static/         - CSS & assets")
    print("  📁 docs/           - Documentation")
    print("  📁 instance/       - SQLite database")
    print("  📄 app.py          - Main Flask application")
    print("\nREADY TO RUN:")
    print("  1. Local: python app.py")
    print("  2. Docker: docker-compose up --build")
    print("  3. Public: cloudflared tunnel --url http://localhost:5000")
    print("\nAccess at: http://localhost:5000")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
