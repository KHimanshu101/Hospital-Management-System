from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from database.connection import get_db_cursor
from mysql.connector import Error

doctors_bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@doctors_bp.route('/')
@login_required
def list_doctors():
    dept_id = request.args.get('department_id', type=int)
    search = request.args.get('search', '').strip()
    
    query = """
        SELECT d.id, d.first_name, d.last_name, d.email, d.phone, d.specialization, 
               d.consultation_fee, d.department_id, dept.name AS department_name
        FROM doctors d
        JOIN departments dept ON d.department_id = dept.id
        WHERE 1=1
    """
    params = []
    
    if dept_id:
        query += " AND d.department_id = %s"
        params.append(dept_id)
    if search:
        query += " AND (d.first_name LIKE %s OR d.last_name LIKE %s OR d.specialization LIKE %s)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    query += " ORDER BY d.last_name, d.first_name"
    
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        doctors = cursor.fetchall()
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        
    return render_template('doctors/list.html', doctors=doctors, departments=departments, selected_dept=dept_id, search=search)

@doctors_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_doctor():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        specialization = request.form.get('specialization', '').strip()
        consultation_fee = request.form.get('consultation_fee', '50.00').strip()
        department_id = request.form.get('department_id', type=int)
        
        if not first_name or not last_name or not email or not phone or not specialization or not department_id:
            flash('All mandatory fields (*) are required.', 'danger')
            return render_template('doctors/form.html', doctor=request.form, departments=departments)
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO doctors (first_name, last_name, email, phone, specialization, consultation_fee, department_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (first_name, last_name, email, phone, specialization, consultation_fee, department_id))
                flash('Doctor added successfully!', 'success')
                return redirect(url_for('doctors.list_doctors'))
        except Error as err:
            flash(f'Database error: {str(err)}', 'danger')
            
    return render_template('doctors/form.html', doctor=None, departments=departments)

@doctors_bp.route('/edit/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
        doctor = cursor.fetchone()
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        departments = cursor.fetchall()
        
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect(url_for('doctors.list_doctors'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        specialization = request.form.get('specialization', '').strip()
        consultation_fee = request.form.get('consultation_fee', '50.00').strip()
        department_id = request.form.get('department_id', type=int)
        
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE doctors 
                    SET first_name = %s, last_name = %s, email = %s, phone = %s, 
                        specialization = %s, consultation_fee = %s, department_id = %s
                    WHERE id = %s
                """, (first_name, last_name, email, phone, specialization, consultation_fee, department_id, doctor_id))
                flash('Doctor updated successfully!', 'success')
                return redirect(url_for('doctors.list_doctors'))
        except Error as err:
            flash(f'Error updating doctor profile: {str(err)}', 'danger')
            
    return render_template('doctors/form.html', doctor=doctor, departments=departments, is_edit=True)

@doctors_bp.route('/delete/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
            flash('Doctor profile deleted.', 'info')
    except Error as err:
        flash(f'Cannot delete doctor with assigned appointments or patients ({str(err)}).', 'danger')
        
    return redirect(url_for('doctors.list_doctors'))
