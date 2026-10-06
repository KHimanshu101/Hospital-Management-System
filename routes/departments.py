from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from database.connection import get_db_cursor
from mysql.connector import Error

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

@departments_bp.route('/')
@login_required
def list_departments():
    query = """
        SELECT d.id, d.name, d.code, d.description, d.created_at,
               COUNT(doc.id) AS total_doctors
        FROM departments d
        LEFT JOIN doctors doc ON d.id = doc.department_id
        GROUP BY d.id, d.name, d.code, d.description, d.created_at
        ORDER BY d.name
    """
    with get_db_cursor() as cursor:
        cursor.execute(query)
        departments = cursor.fetchall()
        
    return render_template('departments/list.html', departments=departments)

@departments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_department():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        
        if not name or not code:
            flash('Department Name and Code are required.', 'danger')
            return render_template('departments/form.html', department=request.form)
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("INSERT INTO departments (name, code, description) VALUES (%s, %s, %s)",
                               (name, code, description))
                flash('Department created successfully!', 'success')
                return redirect(url_for('departments.list_departments'))
        except Error as err:
            flash(f'Error creating department: {str(err)}', 'danger')
            
    return render_template('departments/form.html', department=None)

@departments_bp.route('/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM departments WHERE id = %s", (dept_id,))
        department = cursor.fetchone()
        
    if not department:
        flash('Department not found.', 'danger')
        return redirect(url_for('departments.list_departments'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        description = request.form.get('description', '').strip()
        
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE departments SET name = %s, code = %s, description = %s WHERE id = %s
                """, (name, code, description, dept_id))
                flash('Department updated successfully!', 'success')
                return redirect(url_for('departments.list_departments'))
        except Error as err:
            flash(f'Error updating department: {str(err)}', 'danger')
            
    return render_template('departments/form.html', department=department, is_edit=True)
