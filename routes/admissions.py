from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from services.admission_service import AdmissionService
from database.connection import get_db_cursor

admissions_bp = Blueprint('admissions', __name__, url_prefix='/admissions')

@admissions_bp.route('/')
@login_required
def list_admissions():
    status_filter = request.args.get('status', '').strip()
    admissions = AdmissionService.get_all_admissions(status_filter=status_filter or None)
    return render_template('admissions/list.html', admissions=admissions, selected_status=status_filter)

@admissions_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_admission():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM patients ORDER BY first_name")
        patients = cursor.fetchall()
        
        cursor.execute("SELECT id, CONCAT('Dr. ', first_name, ' ', last_name, ' (', specialization, ')') AS name FROM doctors ORDER BY first_name")
        doctors = cursor.fetchall()
        
    available_beds = AdmissionService.get_available_beds()
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        bed_id = request.form.get('bed_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        reason = request.form.get('reason', '').strip()
        
        if not patient_id or not bed_id or not doctor_id:
            flash('Please select patient, bed, and attending doctor.', 'danger')
            return render_template('admissions/form.html', patients=patients, doctors=doctors, beds=available_beds)
            
        success, result = AdmissionService.create_admission(patient_id, bed_id, doctor_id, reason)
        if success:
            flash('Patient admitted successfully and bed status set to Occupied!', 'success')
            return redirect(url_for('admissions.list_admissions'))
        else:
            flash(f'Admission Error: {result}', 'danger')
            
    return render_template('admissions/form.html', patients=patients, doctors=doctors, beds=available_beds)

@admissions_bp.route('/discharge/<int:admission_id>', methods=['POST'])
@login_required
def discharge(admission_id):
    success, message = AdmissionService.discharge_patient(admission_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admissions.list_admissions'))
