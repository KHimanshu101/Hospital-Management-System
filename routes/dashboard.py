from flask import Blueprint, render_template
from routes.auth import login_required
from database.connection import get_db_cursor
import logging

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    metrics = {
        'total_patients': 0,
        'total_doctors': 0,
        'total_departments': 0,
        'todays_appointments': 0,
        'active_admissions': 0,
        'available_beds': 0,
        'pending_bills': 0,
        'low_stock_medicines': 0
    }
    recent_appointments = []
    bed_types_summary = []
    
    try:
        with get_db_cursor() as cursor:
            # 1. Patients Count
            cursor.execute("SELECT COUNT(*) AS total FROM patients")
            metrics['total_patients'] = cursor.fetchone()['total']
            
            # 2. Doctors Count
            cursor.execute("SELECT COUNT(*) AS total FROM doctors")
            metrics['total_doctors'] = cursor.fetchone()['total']
            
            # 3. Departments Count
            cursor.execute("SELECT COUNT(*) AS total FROM departments")
            metrics['total_departments'] = cursor.fetchone()['total']
            
            # 4. Today's Appointments Count
            cursor.execute("SELECT COUNT(*) AS total FROM appointments WHERE appointment_date = CURRENT_DATE")
            metrics['todays_appointments'] = cursor.fetchone()['total']
            
            # 5. Active Admissions Count
            cursor.execute("SELECT COUNT(*) AS total FROM admissions WHERE status = 'Active'")
            metrics['active_admissions'] = cursor.fetchone()['total']
            
            # 6. Available Beds Count
            cursor.execute("SELECT COUNT(*) AS total FROM rooms_beds WHERE status = 'Available'")
            metrics['available_beds'] = cursor.fetchone()['total']
            
            # 7. Pending Bills Count
            cursor.execute("SELECT COUNT(*) AS total FROM bills WHERE payment_status IN ('Pending', 'Partial')")
            metrics['pending_bills'] = cursor.fetchone()['total']
            
            # 8. Low-Stock Medicines Count (quantity <= reorder_level)
            cursor.execute("SELECT COUNT(*) AS total FROM medicines WHERE quantity <= reorder_level")
            metrics['low_stock_medicines'] = cursor.fetchone()['total']
            
            # Recent appointments list (last 5)
            cursor.execute("""
                SELECT 
                    a.id,
                    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                    CONCAT('Dr. ', doc.first_name, ' ', doc.last_name) AS doctor_name,
                    dept.name AS department_name,
                    a.appointment_date,
                    a.appointment_time,
                    a.status
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors doc ON a.doctor_id = doc.id
                JOIN departments dept ON a.department_id = dept.id
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
                LIMIT 5
            """)
            recent_appointments = cursor.fetchall()
            
            # Bed status summary by room type
            cursor.execute("""
                SELECT 
                    room_type,
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available,
                    SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied
                FROM rooms_beds
                GROUP BY room_type
            """)
            bed_types_summary = cursor.fetchall()

    except Exception as e:
        logger.error(f"Error loading dashboard metrics: {e}")
        
    return render_template('dashboard.html', 
                           metrics=metrics, 
                           recent_appointments=recent_appointments,
                           bed_types_summary=bed_types_summary)
