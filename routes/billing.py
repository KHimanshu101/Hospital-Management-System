from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from services.billing_service import BillingService
from database.connection import get_db_cursor

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/')
@login_required
def list_bills():
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    bills = BillingService.get_all_bills(status_filter=status_filter or None, search=search or None)
    return render_template('billing/list.html', bills=bills, selected_status=status_filter, search=search)

@billing_bp.route('/view/<int:bill_id>')
@login_required
def view_bill(bill_id):
    bill, items = BillingService.get_bill_details(bill_id)
    if not bill:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('billing.list_bills'))
    return render_template('billing/view.html', bill=bill, items=items)

@billing_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_bill():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, CONCAT(first_name, ' ', last_name, ' (Phone: ', phone, ')') AS name FROM patients ORDER BY first_name")
        patients = cursor.fetchall()
        
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        if not patient_id:
            flash('Please select a patient.', 'danger')
            return render_template('billing/form.html', patients=patients)
            
        success, bill_id = BillingService.create_bill(patient_id)
        if success:
            flash('Invoice container created! Add itemized charges below.', 'success')
            return redirect(url_for('billing.view_bill', bill_id=bill_id))
        else:
            flash(bill_id, 'danger')
            
    return render_template('billing/form.html', patients=patients)

@billing_bp.route('/add-item/<int:bill_id>', methods=['POST'])
@login_required
def add_item(bill_id):
    description = request.form.get('description', '').strip()
    amount = request.form.get('amount', type=float)
    quantity = request.form.get('quantity', type=int, default=1)
    item_type = request.form.get('item_type', 'Misc').strip()
    
    if not description or amount is None or amount < 0 or quantity < 1:
        flash('Invalid charge item details.', 'danger')
        return redirect(url_for('billing.view_bill', bill_id=bill_id))
        
    success, message = BillingService.add_bill_item(bill_id, description, amount, quantity, item_type)
    if success:
        flash('Line item added and invoice total updated!', 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('billing.view_bill', bill_id=bill_id))

@billing_bp.route('/payment/<int:bill_id>', methods=['POST'])
@login_required
def pay_bill(bill_id):
    payment_amount = request.form.get('amount', type=float)
    if payment_amount is None or payment_amount <= 0:
        flash('Enter a valid payment amount.', 'danger')
        return redirect(url_for('billing.view_bill', bill_id=bill_id))
        
    success, message = BillingService.record_payment(bill_id, payment_amount)
    if success:
        flash('Payment recorded successfully!', 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('billing.view_bill', bill_id=bill_id))
