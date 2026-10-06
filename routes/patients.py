from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from database.connection import get_db_cursor
from mysql.connector import Error

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('/')
@login_required
def list_patients():
    search = request.args.get('search', '').strip()
    query = "SELECT * FROM patients WHERE 1=1"
    params = []
    
    if search:
        query += " AND (first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s OR email LIKE %s)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
        
    query += " ORDER BY id DESC"
    
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        patients = cursor.fetchall()
        
    return render_template('patients/list.html', patients=patients, search=search)

@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        
        if not first_name or not last_name or not dob or not gender or not phone:
            flash('Please fill in all mandatory fields (*).', 'danger')
            return render_template('patients/form.html', patient=request.form)
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO patients (first_name, last_name, dob, gender, phone, email, address, emergency_contact)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (first_name, last_name, dob, gender, phone, email or None, address, emergency_contact))
                flash('Patient registered successfully!', 'success')
                return redirect(url_for('patients.list_patients'))
        except Error as err:
            flash(f'Database error: {str(err)}', 'danger')
            
    return render_template('patients/form.html', patient=None)

@patients_bp.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        
    if not patient:
        flash('Patient record not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        dob = request.form.get('dob', '').strip()
        gender = request.form.get('gender', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        
        if not first_name or not last_name or not dob or not gender or not phone:
            flash('Please fill in all required fields.', 'danger')
            return render_template('patients/form.html', patient=request.form, is_edit=True)
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE patients 
                    SET first_name = %s, last_name = %s, dob = %s, gender = %s,
                        phone = %s, email = %s, address = %s, emergency_contact = %s
                    WHERE id = %s
                """, (first_name, last_name, dob, gender, phone, email or None, address, emergency_contact, patient_id))
                flash('Patient updated successfully!', 'success')
                return redirect(url_for('patients.list_patients'))
        except Error as err:
            flash(f'Error updating patient: {str(err)}', 'danger')
            
    return render_template('patients/form.html', patient=patient, is_edit=True)

@patients_bp.route('/delete/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
            flash('Patient record deleted.', 'info')
    except Error as err:
        flash(f'Cannot delete patient with active appointments or medical records ({str(err)}).', 'danger')
        
    return redirect(url_for('patients.list_patients'))
