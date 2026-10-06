from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from services.pharmacy_service import PharmacyService
from database.connection import get_db_cursor

pharmacy_bp = Blueprint('pharmacy', __name__, url_prefix='/pharmacy')

@pharmacy_bp.route('/')
@login_required
def list_medicines():
    search = request.args.get('search', '').strip()
    low_stock = request.args.get('low_stock', type=bool, default=False)
    
    medicines = PharmacyService.get_all_medicines(search=search or None, low_stock_only=low_stock)
    return render_template('pharmacy/list.html', medicines=medicines, search=search, low_stock=low_stock)

@pharmacy_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_medicine():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        batch_number = request.form.get('batch_number', '').strip()
        quantity = request.form.get('quantity', type=int, default=0)
        expiry_date = request.form.get('expiry_date', '').strip()
        unit_price = request.form.get('unit_price', type=float, default=0.0)
        reorder_level = request.form.get('reorder_level', type=int, default=10)
        
        if not name or not batch_number or not expiry_date:
            flash('Name, Batch Number, and Expiry Date are mandatory.', 'danger')
            return render_template('pharmacy/form.html', medicine=request.form)
            
        success, result = PharmacyService.add_medicine(name, batch_number, quantity, expiry_date, unit_price, reorder_level)
        if success:
            flash('Medicine added to inventory successfully!', 'success')
            return redirect(url_for('pharmacy.list_medicines'))
        else:
            flash(result, 'danger')
            
    return render_template('pharmacy/form.html', medicine=None)

@pharmacy_bp.route('/dispense', methods=['GET', 'POST'])
@login_required
def dispense_prescription():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM patients ORDER BY first_name")
        patients = cursor.fetchall()
        
        cursor.execute("SELECT id, CONCAT('Dr. ', first_name, ' ', last_name) AS name FROM doctors ORDER BY first_name")
        doctors = cursor.fetchall()
        
        cursor.execute("SELECT id, name, batch_number, quantity, unit_price FROM medicines WHERE quantity > 0 ORDER BY name")
        medicines = cursor.fetchall()
        
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        appointment_id = request.form.get('appointment_id', type=int) or None
        notes = request.form.get('notes', '').strip()
        
        med_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')
        dosages = request.form.getlist('dosage[]')
        
        items = []
        for m_id, q_val, d_val in zip(med_ids, quantities, dosages):
            if m_id and q_val and int(q_val) > 0:
                items.append({
                    'medicine_id': int(m_id),
                    'quantity': int(q_val),
                    'dosage': d_val.strip()
                })
                
        if not patient_id or not doctor_id or not items:
            flash('Please select patient, doctor, and at least one valid medicine with quantity > 0.', 'danger')
            return render_template('pharmacy/dispense.html', patients=patients, doctors=doctors, medicines=medicines)
            
        success, result = PharmacyService.create_prescription_and_dispense(patient_id, doctor_id, appointment_id, items, notes)
        if success:
            flash(f'Prescription #{result} dispensed! Stock deducted and bill updated.', 'success')
            return redirect(url_for('pharmacy.list_medicines'))
        else:
            flash(f'Dispensing Error: {result}', 'danger')
            
    return render_template('pharmacy/dispense.html', patients=patients, doctors=doctors, medicines=medicines)
