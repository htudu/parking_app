from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from backend.extensions import db
from backend.models import ParkingSlot, Reservation, User
from backend.utils import generate_qr_code, get_reservation_summary


slots_bp = Blueprint('slots', __name__, url_prefix='/slots')
reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')


# ==================== PARKING SLOTS ROUTES ====================

@slots_bp.route('/')
@slots_bp.route('/list')
@login_required
def list_slots():
    """List all parking slots with availability"""
    slots = ParkingSlot.query.order_by(ParkingSlot.slot_number).all()
    return render_template('slots.html', slots=slots)


@slots_bp.route('/available')
@login_required
def available_slots():
    """List only available parking slots"""
    slots = ParkingSlot.query.filter_by(is_available=True).order_by(ParkingSlot.slot_number).all()
    return render_template('slots.html', slots=slots, filter_type='available')


# ==================== RESERVATION ROUTES ====================

@reservations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_reservation():
    """Create a new reservation"""
    if request.method == 'GET':
        slot_id = request.args.get('slot_id', type=int)
        slot = ParkingSlot.query.get_or_404(slot_id) if slot_id else None
        
        if slot and not slot.is_available:
            flash('This slot is no longer available', 'error')
            return redirect(url_for('slots.list_slots'))
        
        return render_template('reservation_create.html', slot=slot)
    
    # POST: Process reservation
    slot_id = request.form.get('slot_id', type=int)
    
    if not slot_id:
        flash('Invalid slot selected', 'error')
        return redirect(url_for('slots.list_slots'))
    
    try:
        # Fetch slot with locking to prevent race conditions
        slot = ParkingSlot.query.filter_by(id=slot_id).first()
        
        if not slot:
            flash('Slot not found', 'error')
            return redirect(url_for('slots.list_slots'))
        
        if not slot.is_available:
            flash('This slot has already been reserved', 'error')
            return redirect(url_for('slots.list_slots'))
        
        # Create reservation
        reservation = Reservation(
            user_id=current_user.id,
            slot_id=slot_id
        )
        
        # Mark slot as unavailable
        slot.is_available = False
        
        db.session.add(reservation)
        db.session.commit()
        
        # Generate QR code
        qr_image_data, qr_payload = generate_qr_code(
            reservation.id,
            current_user.email,
            slot.slot_number,
            reservation.reserved_at
        )
        
        # Store QR payload in database
        reservation.qr_code_data = qr_payload
        db.session.commit()
        
        flash('Reservation successful!', 'success')
        return redirect(url_for('reservations.view_reservation', reservation_id=reservation.id))
    
    except IntegrityError:
        db.session.rollback()
        flash('Slot already reserved. Please choose another.', 'error')
        return redirect(url_for('slots.list_slots'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Reservation error: {str(e)}')
        flash('Reservation failed. Please try again.', 'error')
        return redirect(url_for('slots.list_slots'))


@reservations_bp.route('/<int:reservation_id>')
@login_required
def view_reservation(reservation_id):
    """View reservation with QR code"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Authorization check: user can only view their own reservations
    if reservation.user_id != current_user.id:
        flash('You do not have permission to view this reservation', 'error')
        return redirect(url_for('slots.list_slots'))
    
    # Generate QR code if not already stored
    if not reservation.qr_code_data:
        qr_image_data, qr_payload = generate_qr_code(
            reservation.id,
            reservation.user.email,
            reservation.slot.slot_number,
            reservation.reserved_at
        )
        reservation.qr_code_data = qr_payload
        db.session.commit()
    else:
        qr_image_data, _ = generate_qr_code(
            reservation.id,
            reservation.user.email,
            reservation.slot.slot_number,
            reservation.reserved_at
        )
    
    summary = get_reservation_summary(reservation)
    
    return render_template('reservation_success.html', 
                         reservation=reservation, 
                         qr_image=qr_image_data,
                         summary=summary)


@reservations_bp.route('/<int:reservation_id>/checkout', methods=['GET', 'POST'])
@login_required
def checkout_reservation(reservation_id):
    """Checkout a reservation and release the parking slot"""
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Authorization check
    if reservation.user_id != current_user.id:
        flash('You do not have permission to checkout this reservation', 'error')
        return redirect(url_for('slots.list_slots'))
    
    if request.method == 'GET':
        # Show confirmation page
        return render_template('checkout_reservation.html', reservation=reservation)
    
    # POST: Process checkout
    try:
        slot = reservation.slot
        slot_number = slot.slot_number
        
        # Mark slot as available
        slot.is_available = True
        
        # Delete reservation
        db.session.delete(reservation)
        db.session.commit()
        
        flash(f'You have successfully checked out from slot {slot_number}. Slot is now available.', 'success')
        return redirect(url_for('slots.list_slots'))
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Checkout error: {str(e)}')
        flash('Failed to checkout reservation. Please try again.', 'error')
        return redirect(url_for('reservations.view_reservation', reservation_id=reservation_id))


@reservations_bp.route('')
@login_required
def my_reservations():
    """View all user's reservations"""
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(
        Reservation.reserved_at.desc()
    ).all()
    
    summaries = [get_reservation_summary(r) for r in reservations]
    
    return render_template('my_reservations.html', reservations=summaries)
