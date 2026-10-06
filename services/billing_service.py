from database.connection import get_db_cursor
from mysql.connector import Error

class BillingService:
    @staticmethod
    def get_all_bills(status_filter=None, search=None):
        """Retrieve invoices with patient info, payment status, and breakdown."""
        query = """
            SELECT 
                b.id,
                b.patient_id,
                CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                p.phone AS patient_phone,
                b.admission_id,
                b.bill_date,
                b.total_amount,
                b.paid_amount,
                (b.total_amount - b.paid_amount) AS balance_due,
                b.payment_status
            FROM bills b
            JOIN patients p ON b.patient_id = p.id
            WHERE 1=1
        """
        params = []
        if status_filter:
            query += " AND b.payment_status = %s"
            params.append(status_filter)
        if search:
            query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
            
        query += " ORDER BY b.bill_date DESC"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_bill_details(bill_id):
        """Fetch invoice header and itemized line items."""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    b.id,
                    b.patient_id,
                    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
                    p.email AS patient_email,
                    p.phone AS patient_phone,
                    b.admission_id,
                    b.bill_date,
                    b.total_amount,
                    b.paid_amount,
                    (b.total_amount - b.paid_amount) AS balance_due,
                    b.payment_status
                FROM bills b
                JOIN patients p ON b.patient_id = p.id
                WHERE b.id = %s
            """, (bill_id,))
            bill = cursor.fetchone()
            
            if not bill:
                return None, []
                
            cursor.execute("""
                SELECT id, description, amount, quantity, item_type, (amount * quantity) AS line_total
                FROM bill_items
                WHERE bill_id = %s
            """, (bill_id,))
            items = cursor.fetchall()
            
            return bill, items

    @staticmethod
    def create_bill(patient_id, admission_id=None):
        """Create a new invoice container for a patient."""
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO bills (patient_id, admission_id, bill_date, total_amount, paid_amount, payment_status)
                    VALUES (%s, %s, NOW(), 0.00, 0.00, 'Pending')
                """, (patient_id, admission_id))
                return True, cursor.lastrowid
        except Error as err:
            return False, f"Error creating bill: {str(err)}"

    @staticmethod
    def add_bill_item(bill_id, description, amount, quantity=1, item_type='Misc'):
        """Add an itemized charge to a bill and recalculate total balance inside a transaction."""
        with get_db_cursor(commit=False) as cursor:
            try:
                # Insert bill item
                cursor.execute("""
                    INSERT INTO bill_items (bill_id, description, amount, quantity, item_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (bill_id, description, amount, quantity, item_type))
                
                # Recalculate total sum
                cursor.execute("SELECT SUM(amount * quantity) AS new_total FROM bill_items WHERE bill_id = %s", (bill_id,))
                new_total = cursor.fetchone()['new_total'] or 0.00
                
                cursor.execute("SELECT paid_amount FROM bills WHERE id = %s", (bill_id,))
                paid = cursor.fetchone()['paid_amount'] or 0.00
                
                # Determine new payment status
                if paid >= new_total and new_total > 0:
                    status = 'Paid'
                elif paid > 0:
                    status = 'Partial'
                else:
                    status = 'Pending'
                    
                cursor.execute("""
                    UPDATE bills 
                    SET total_amount = %s, payment_status = %s 
                    WHERE id = %s
                """, (new_total, status, bill_id))
                
                cursor.execute("COMMIT")
                return True, "Item added successfully."
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Failed to add bill item: {str(err)}"

    @staticmethod
    def record_payment(bill_id, payment_amount):
        """Record a financial payment against a bill balance."""
        if payment_amount <= 0:
            return False, "Payment amount must be greater than zero."
            
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT total_amount, paid_amount FROM bills WHERE id = %s FOR UPDATE", (bill_id,))
            bill = cursor.fetchone()
            
            if not bill:
                return False, "Bill not found."
                
            new_paid = float(bill['paid_amount']) + float(payment_amount)
            total = float(bill['total_amount'])
            
            if new_paid >= total:
                status = 'Paid'
            elif new_paid > 0:
                status = 'Partial'
            else:
                status = 'Pending'
                
            try:
                cursor.execute("""
                    UPDATE bills 
                    SET paid_amount = %s, payment_status = %s 
                    WHERE id = %s
                """, (new_paid, status, bill_id))
                cursor.execute("COMMIT")
                return True, "Payment recorded successfully."
            except Error as err:
                cursor.execute("ROLLBACK")
                return False, f"Payment recording failed: {str(err)}"
