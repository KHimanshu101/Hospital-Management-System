from database.connection import get_db_cursor
from mysql.connector import Error

class PharmacyService:
    @staticmethod
    def get_all_medicines(search=None, low_stock_only=False):
        """Retrieve pharmacy inventory list with optional search and low-stock filter."""
        query = """
            SELECT id, name, batch_number, quantity, expiry_date, unit_price, reorder_level,
                   (quantity <= reorder_level) AS is_low_stock
            FROM medicines
            WHERE 1=1
        """
        params = []
        if low_stock_only:
            query += " AND quantity <= reorder_level"
        if search:
            query += " AND (name LIKE %s OR batch_number LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
            
        query += " ORDER BY name ASC"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def add_medicine(name, batch_number, quantity, expiry_date, unit_price, reorder_level=10):
        """Add new medicine stock to pharmacy inventory."""
        if int(quantity) < 0 or float(unit_price) < 0:
            return False, "Quantity and price cannot be negative."
            
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO medicines (name, batch_number, quantity, expiry_date, unit_price, reorder_level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, batch_number, quantity, expiry_date, unit_price, reorder_level))
                return True, cursor.lastrowid
        except Error as err:
            return False, f"Failed to add medicine: {str(err)}"

    @staticmethod
    def update_stock(medicine_id, quantity_change):
        """Increase or decrease medicine stock."""
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT quantity FROM medicines WHERE id = %s FOR UPDATE", (medicine_id,))
            med = cursor.fetchone()
            if not med:
                return False, "Medicine not found."
                
            new_qty = med['quantity'] + int(quantity_change)
            if new_qty < 0:
                return False, "Stock deduction would result in negative inventory quantity."
                
            try:
                cursor.execute("UPDATE medicines SET quantity = %s WHERE id = %s", (new_qty, medicine_id))
                cursor.execute("COMMIT")
                return True, "Stock updated successfully."
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Stock update failed: {str(err)}"

    @staticmethod
    def create_prescription_and_dispense(patient_id, doctor_id, appointment_id, items, notes=""):
        """
        Dispense medicine prescription in an atomic transaction:
        1. Validates stock for all items
        2. Creates prescription header & items
        3. Deducts stock quantities
        4. Adds medicine charges to patient's active bill (or creates new bill)
        """
        if not items:
            return False, "Prescription must contain at least one medicine item."
            
        with get_db_cursor(commit=False) as cursor:
            try:
                # 1. Verify stock availability for all items
                for item in items:
                    med_id = item['medicine_id']
                    req_qty = int(item['quantity'])
                    cursor.execute("SELECT name, quantity, unit_price FROM medicines WHERE id = %s FOR UPDATE", (med_id,))
                    med = cursor.fetchone()
                    if not med:
                        cursor.execute("ROLLBACK")
                        return False, f"Medicine ID {med_id} not found."
                    if med['quantity'] < req_qty:
                        cursor.execute("ROLLBACK")
                        return False, f"Insufficient stock for '{med['name']}'. Requested: {req_qty}, Available: {med['quantity']}"
                    item['unit_price'] = float(med['unit_price'])
                    item['total_price'] = item['unit_price'] * req_qty

                # 2. Insert prescription header
                cursor.execute("""
                    INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, prescription_date, notes)
                    VALUES (%s, %s, %s, NOW(), %s)
                """, (appointment_id, patient_id, doctor_id, notes))
                prescription_id = cursor.lastrowid

                # 3. Insert prescription line items and deduct medicine stock
                total_dispense_amount = 0.0
                for item in items:
                    cursor.execute("""
                        INSERT INTO prescription_items (prescription_id, medicine_id, quantity, dosage, unit_price, total_price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (prescription_id, item['medicine_id'], item['quantity'], item.get('dosage', ''), item['unit_price'], item['total_price']))
                    
                    cursor.execute("UPDATE medicines SET quantity = quantity - %s WHERE id = %s", (item['quantity'], item['medicine_id']))
                    total_dispense_amount += item['total_price']

                # 4. Attach to open bill or create new bill for patient
                cursor.execute("SELECT id FROM bills WHERE patient_id = %s AND payment_status != 'Paid' ORDER BY bill_date DESC LIMIT 1", (patient_id,))
                open_bill = cursor.fetchone()
                
                if open_bill:
                    bill_id = open_bill['id']
                else:
                    cursor.execute("""
                        INSERT INTO bills (patient_id, bill_date, total_amount, paid_amount, payment_status)
                        VALUES (%s, NOW(), 0.00, 0.00, 'Pending')
                    """, (patient_id,))
                    bill_id = cursor.lastrowid
                    
                cursor.execute("""
                    INSERT INTO bill_items (bill_id, description, amount, quantity, item_type)
                    VALUES (%s, %s, %s, 1, 'Medicine')
                """, (bill_id, f"Prescription #{prescription_id} Dispensed Medicines", total_dispense_amount))

                # Update bill total
                cursor.execute("""
                    UPDATE bills 
                    SET total_amount = total_amount + %s 
                    WHERE id = %s
                """, (total_dispense_amount, bill_id))

                cursor.execute("COMMIT")
                return True, prescription_id
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Prescription dispensing failed: {str(err)}"
