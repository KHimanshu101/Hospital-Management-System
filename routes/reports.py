from flask import Blueprint, render_template
from routes.auth import login_required
from database.connection import get_db_cursor

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    doctor_workload = []
    department_stats = []
    bed_occupancy = []
    monthly_revenue = []
    low_stock = []
    
    with get_db_cursor() as cursor:
        # 1. Doctor Workload Report
        cursor.execute("""
            SELECT d.id, CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
                   dept.name AS department_name,
                   COUNT(DISTINCT a.id) AS total_appointments,
                   COUNT(DISTINCT adm.id) AS total_admissions
            FROM doctors d
            JOIN departments dept ON d.department_id = dept.id
            LEFT JOIN appointments a ON d.id = a.doctor_id
            LEFT JOIN admissions adm ON d.id = adm.doctor_id
            GROUP BY d.id, d.first_name, d.last_name, dept.name
            ORDER BY total_appointments DESC
        """)
        doctor_workload = cursor.fetchall()
        
        # 2. Department Patient Distribution
        cursor.execute("""
            SELECT dept.name AS department_name,
                   COUNT(DISTINCT doc.id) AS doctor_count,
                   COUNT(DISTINCT appt.id) AS appointment_count
            FROM departments dept
            LEFT JOIN doctors doc ON dept.id = doc.department_id
            LEFT JOIN appointments appt ON dept.id = appt.department_id
            GROUP BY dept.id, dept.name
            ORDER BY appointment_count DESC
        """)
        department_stats = cursor.fetchall()
        
        # 3. Bed Occupancy Matrix
        cursor.execute("""
            SELECT room_type,
                   COUNT(*) AS total_beds,
                   SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available,
                   SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied
            FROM rooms_beds
            GROUP BY room_type
        """)
        bed_occupancy = cursor.fetchall()
        
        # 4. Financial Summary
        cursor.execute("""
            SELECT payment_status,
                   COUNT(*) AS invoice_count,
                   SUM(total_amount) AS total_billed,
                   SUM(paid_amount) AS total_collected
            FROM bills
            GROUP BY payment_status
        """)
        monthly_revenue = cursor.fetchall()
        
        # 5. Low Stock Alert Items
        cursor.execute("""
            SELECT name, batch_number, quantity, reorder_level, unit_price
            FROM medicines
            WHERE quantity <= reorder_level
            ORDER BY quantity ASC
        """)
        low_stock = cursor.fetchall()
        
    return render_template('reports/index.html',
                           doctor_workload=doctor_workload,
                           department_stats=department_stats,
                           bed_occupancy=bed_occupancy,
                           monthly_revenue=monthly_revenue,
                           low_stock=low_stock)
