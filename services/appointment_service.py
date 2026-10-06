from database.connection import get_db_cursor
from mysql.connector import Error
import datetime

class AppointmentService:
    @staticmethod
    def is_doctor_available(doctor_id, appt_date, appt_time, exclude_id=None):
        """
        Check if the doctor already has a scheduled appointment at the given date and time slot.
        Prevents double-booking collisions.
        """
        query = """
            SELECT id FROM appointments 
            WHERE doctor_id = %s 
              AND appointment_date = %s 
              AND appointment_time = %s 
              AND status = 'Scheduled'
        """
        params = [doctor_id, appt_date, appt_time]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
            
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            match = cursor.fetchone()
            return match is None

    @staticmethod
    def create_appointment(patient_id, doctor_id, department_id, appt_date, appt_time, reason=""):
        """
        Create a new appointment after verifying doctor availability.
        Returns (success: bool, message_or_id)
        """
        if not AppointmentService.is_doctor_available(doctor_id, appt_date, appt_time):
            return False, "Conflict detected: Doctor already has a scheduled appointment at this exact date and time slot."
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO appointments 
                    (patient_id, doctor_id, department_id, appointment_date, appointment_time, reason, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
                """, (patient_id, doctor_id, department_id, appt_date, appt_time, reason))
                return True, cursor.lastrowid
        except Error as err:
            return False, f"Database error creating appointment: {str(err)}"

    @staticmethod
    def get_all_appointments(date_filter=None, doctor_filter=None, status_filter=None, search=None):
        """Fetch list of appointments with filters and patient/doctor details."""
        query = """
            SELECT 
                a.id,
                a.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                p.phone AS patient_phone,
                a.doctor_id,
                CONCAT('Dr. ', doc.first_name, ' ', doc.last_name) AS doctor_name,
                a.department_id,
                dept.name AS department_name,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors doc ON a.doctor_id = doc.id
            JOIN departments dept ON a.department_id = dept.id
            WHERE 1=1
        """
        params = []
        if date_filter:
            query += " AND a.appointment_date = %s"
            params.append(date_filter)
        if doctor_filter:
            query += " AND a.doctor_id = %s"
            params.append(doctor_filter)
        if status_filter:
            query += " AND a.status = %s"
            params.append(status_filter)
        if search:
            query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s OR doc.first_name LIKE %s OR doc.last_name LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term, search_term])
            
        query += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def update_status(appointment_id, new_status):
        """Update appointment status (e.g., Scheduled, Completed, Cancelled)."""
        valid_statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
        if new_status not in valid_statuses:
            return False, "Invalid appointment status."
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("UPDATE appointments SET status = %s WHERE id = %s", (new_status, appointment_id))
                return True, "Status updated successfully."
        except Error as err:
            return False, f"Failed to update appointment: {str(err)}"
