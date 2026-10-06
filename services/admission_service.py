from database.connection import get_db_cursor
from mysql.connector import Error

class AdmissionService:
    @staticmethod
    def get_available_beds():
        """Retrieve list of beds currently available for inpatient admission."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, room_number, bed_number, room_type, daily_rate 
                FROM rooms_beds 
                WHERE status = 'Available'
                ORDER BY room_number, bed_number
            """)
            return cursor.fetchall()

    @staticmethod
    def create_admission(patient_id, bed_id, doctor_id, reason=""):
        """
        Admit a patient to an available bed using a transaction.
        Updates bed status to 'Occupied' and records active admission.
        """
        with get_db_cursor(commit=False) as cursor:
            # 1. Verify bed is currently available
            cursor.execute("SELECT status, daily_rate FROM rooms_beds WHERE id = %s FOR UPDATE", (bed_id,))
            bed = cursor.fetchone()
            
            if not bed:
                return False, "Selected bed does not exist."
            if bed['status'] != 'Available':
                return False, "Bed conflict: Selected bed is not available (occupied or in maintenance)."
                
            # 2. Verify patient does not already have an active admission
            cursor.execute("SELECT id FROM admissions WHERE patient_id = %s AND status = 'Active'", (patient_id,))
            if cursor.fetchone():
                return False, "Patient is already actively admitted in another bed."
                
            try:
                # 3. Mark bed as occupied
                cursor.execute("UPDATE rooms_beds SET status = 'Occupied' WHERE id = %s", (bed_id,))
                
                # 4. Insert admission record
                cursor.execute("""
                    INSERT INTO admissions (patient_id, bed_id, doctor_id, admission_date, reason, status)
                    VALUES (%s, %s, %s, NOW(), %s, 'Active')
                """, (patient_id, bed_id, doctor_id, reason))
                
                admission_id = cursor.lastrowid
                
                # 5. Create initial pending bill
                cursor.execute("""
                    INSERT INTO bills (patient_id, admission_id, bill_date, total_amount, paid_amount, payment_status)
                    VALUES (%s, %s, NOW(), 0.00, 0.00, 'Pending')
                """, (patient_id, admission_id))
                
                cursor.execute("COMMIT")
                return True, admission_id
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Admission transaction failed: {str(err)}"

    @staticmethod
    def discharge_patient(admission_id):
        """
        Discharge an admitted patient, releasing their assigned bed back to 'Available'.
        """
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT patient_id, bed_id, status FROM admissions WHERE id = %s FOR UPDATE", (admission_id,))
            adm = cursor.fetchone()
            
            if not adm:
                return False, "Admission record not found."
            if adm['status'] == 'Discharged':
                return False, "Patient has already been discharged."
                
            try:
                # 1. Mark admission as Discharged
                cursor.execute("""
                    UPDATE admissions 
                    SET discharge_date = NOW(), status = 'Discharged' 
                    WHERE id = %s
                """, (admission_id,))
                
                # 2. Release bed back to Available
                cursor.execute("UPDATE rooms_beds SET status = 'Available' WHERE id = %s", (adm['bed_id'],))
                
                cursor.execute("COMMIT")
                return True, "Patient discharged successfully and bed released."
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Discharge failed: {str(err)}"

    @staticmethod
    def get_all_admissions(status_filter=None):
        """Fetch admissions list with patient, bed, doctor, and billing info."""
        query = """
            SELECT 
                adm.id,
                adm.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                p.phone AS patient_phone,
                adm.bed_id,
                rb.room_number,
                rb.bed_number,
                rb.room_type,
                rb.daily_rate,
                adm.doctor_id,
                CONCAT('Dr. ', doc.first_name, ' ', doc.last_name) AS doctor_name,
                adm.admission_date,
                adm.discharge_date,
                adm.reason,
                adm.status
            FROM admissions adm
            JOIN patients p ON adm.patient_id = p.id
            JOIN rooms_beds rb ON adm.bed_id = rb.id
            JOIN doctors doc ON adm.doctor_id = doc.id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND adm.status = %s"
            params.append(status_filter)
            
        query += " ORDER BY adm.admission_date DESC"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
