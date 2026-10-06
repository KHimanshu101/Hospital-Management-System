from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from services.appointment_service import AppointmentService
from database.connection import get_db_cursor

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@appointments_bp.route('/')
@login_required
def list_appointments():
    date_filter = request.args.get('date', '').strip()
    doctor_filter = request.args.get('doctor_id', type=int)
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    
    appointments = AppointmentService.get_all_appointments(
        date_filter=date_filter or None,
        doctor_filter=doctor_filter or None,
        status_filter=status_filter or None,
        search=search or None
    )
    
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, CONCAT('Dr. ', first_name, ' ', last_name) AS name FROM doctors ORDER BY last_name")
        doctors = cursor.fetchall()
        
    return render_template('appointments/list.html', 
                           appointments=appointments, 
                           doctors=doctors,
                           selected_date=date_filter,
                           selected_doctor=doctor_filter,
                           selected_status=status_filter,
                           search=search)

@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name, ' (Phone: ', phone, ')') AS name FROM patients ORDER BY first_name")
        patients = cursor.fetchall()
        
        cursor.execute("""
            SELECT d.id, CONCAT('Dr. ', d.first_name, ' ', d.last_name, ' - ', dept.name, ' ($', d.consultation_fee, ')') AS name, d.department_id 
            FROM doctors d 
            JOIN departments dept ON d.department_id = dept.id 
            ORDER BY d.first_name
        """)
        doctors = cursor.fetchall()
        
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        department_id = request.form.get('department_id', type=int)
        appt_date = request.form.get('appointment_date', '').strip()
        appt_time = request.form.get('appointment_time', '').strip()
        reason = request.form.get('reason', '').strip()
        
        if not patient_id or not doctor_id or not department_id or not appt_date or not appt_time:
            flash('All mandatory fields (*) are required.', 'danger')
            return render_template('appointments/form.html', patients=patients, doctors=doctors, departments=departments, form_data=request.form)
            
        success, message = AppointmentService.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            department_id=department_id,
            appt_date=appt_date,
            appt_time=appt_time,
            reason=reason
        )
        
        if success:
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('appointments.list_appointments'))
        else:
            flash(f'Scheduling Conflict Error: {message}', 'danger')
            return render_template('appointments/form.html', patients=patients, doctors=doctors, departments=departments, form_data=request.form)
            
    return render_template('appointments/form.html', patients=patients, doctors=doctors, departments=departments, form_data=None)

@appointments_bp.route('/status/<int:appointment_id>', methods=['POST'])
@login_required
def update_status(appointment_id):
    new_status = request.form.get('status', '').strip()
    success, message = AppointmentService.update_status(appointment_id, new_status)
    if success:
        flash(f'Appointment status changed to {new_status}.', 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('appointments.list_appointments'))
