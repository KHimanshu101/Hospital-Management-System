from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from database.connection import get_db_cursor
from mysql.connector import Error

beds_bp = Blueprint('beds', __name__, url_prefix='/beds')

@beds_bp.route('/')
@login_required
def list_beds():
    type_filter = request.args.get('room_type', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = """
        SELECT rb.id, rb.room_number, rb.bed_number, rb.room_type, rb.daily_rate, rb.status,
               adm.id AS active_admission_id,
               CONCAT(p.first_name, ' ', p.last_name) AS current_patient_name
        FROM rooms_beds rb
        LEFT JOIN admissions adm ON rb.id = adm.bed_id AND adm.status = 'Active'
        LEFT JOIN patients p ON adm.patient_id = p.id
        WHERE 1=1
    """
    params = []
    
    if type_filter:
        query += " AND rb.room_type = %s"
        params.append(type_filter)
    if status_filter:
        query += " AND rb.status = %s"
        params.append(status_filter)
        
    query += " ORDER BY rb.room_number, rb.bed_number"
    
    with get_db_cursor() as cursor:
        cursor.execute(query, params)
        beds = cursor.fetchall()
        
    return render_template('beds/list.html', beds=beds, selected_type=type_filter, selected_status=status_filter)

@beds_bp.route('/add', methods=['POST'])
@login_required
def add_bed():
    room_number = request.form.get('room_number', '').strip()
    bed_number = request.form.get('bed_number', '').strip()
    room_type = request.form.get('room_type', 'General').strip()
    daily_rate = request.form.get('daily_rate', '100.00').strip()
    
    if not room_number or not bed_number:
        flash('Room number and Bed number are required.', 'danger')
        return redirect(url_for('beds.list_beds'))
        
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO rooms_beds (room_number, bed_number, room_type, daily_rate, status)
                VALUES (%s, %s, %s, %s, 'Available')
            """, (room_number, bed_number, room_type, daily_rate))
            flash(f'Bed {room_number}-{bed_number} added successfully!', 'success')
    except Error as err:
        flash(f'Error adding bed: {str(err)}', 'danger')
        
    return redirect(url_for('beds.list_beds'))

@beds_bp.route('/status/<int:bed_id>', methods=['POST'])
@login_required
def update_status(bed_id):
    new_status = request.form.get('status', '').strip()
    
    with get_db_cursor(commit=False) as cursor:
        cursor.execute("SELECT status FROM rooms_beds WHERE id = %s", (bed_id,))
        current = cursor.fetchone()
        
        if current and current['status'] == 'Occupied' and new_status == 'Available':
            flash('Cannot mark occupied bed as Available manually. Discharge patient from admissions module instead.', 'warning')
            return redirect(url_for('beds.list_beds'))
            
        try:
            cursor.execute("UPDATE rooms_beds SET status = %s WHERE id = %s", (new_status, bed_id))
            cursor.execute("COMMIT")
            flash('Bed status updated successfully.', 'success')
        except Error as err:
            cursor.execute("ROLLBACK")
            flash(f'Failed to update bed status: {str(err)}', 'danger')
            
    return redirect(url_for('beds.list_beds'))
