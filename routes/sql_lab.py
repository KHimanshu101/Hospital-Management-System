from flask import Blueprint, render_template, request, flash
from routes.auth import login_required
from database.connection import get_db_cursor
import re

sql_lab_bp = Blueprint('sql_lab', __name__, url_prefix='/sql-lab')

SAMPLE_QUERIES = [
    {
        'id': 'join_doctors_dept',
        'title': '1. INNER JOIN: Doctors with Department Names',
        'category': 'JOIN Operations',
        'explanation': 'Demonstrates an INNER JOIN connecting doctors to their respective departments using foreign key department_id.',
        'query': "SELECT d.id, CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name, d.specialization, d.consultation_fee, dept.name AS department_name FROM doctors d INNER JOIN departments dept ON d.department_id = dept.id ORDER BY dept.name;"
    },
    {
        'id': 'left_join_beds',
        'title': '2. LEFT JOIN: Bed Inventory & Current Patient Admissions',
        'category': 'JOIN Operations',
        'explanation': 'Demonstrates a LEFT JOIN showing all hospital beds and matching active patient admission details if currently occupied.',
        'query': "SELECT rb.room_number, rb.bed_number, rb.room_type, rb.status, CONCAT(p.first_name, ' ', p.last_name) AS occupied_by FROM rooms_beds rb LEFT JOIN admissions adm ON rb.id = adm.bed_id AND adm.status = 'Active' LEFT JOIN patients p ON adm.patient_id = p.id ORDER BY rb.room_number, rb.bed_number;"
    },
    {
        'id': 'subquery_fee',
        'title': '3. Nested Subquery: Doctors charging above average fee',
        'category': 'Subqueries',
        'explanation': 'Evaluates a scalar subquery (AVG fee) in the WHERE clause to filter doctors earning above average consultation fees.',
        'query': "SELECT id, CONCAT('Dr. ', first_name, ' ', last_name) AS doctor_name, specialization, consultation_fee FROM doctors WHERE consultation_fee > (SELECT AVG(consultation_fee) FROM doctors) ORDER BY consultation_fee DESC;"
    },
    {
        'id': 'subquery_active_patients',
        'title': '4. IN Subquery: Patients with Active Admissions',
        'category': 'Subqueries',
        'explanation': 'Uses the IN operator with a nested SELECT to filter patients currently admitted in inpatient care.',
        'query': "SELECT id, CONCAT(first_name, ' ', last_name) AS patient_name, phone, email FROM patients WHERE id IN (SELECT DISTINCT patient_id FROM admissions WHERE status = 'Active');"
    },
    {
        'id': 'group_by_departments',
        'title': '5. GROUP BY & HAVING: Department Doctor Count & Average Fee',
        'category': 'Aggregation & Grouping',
        'explanation': 'Aggregates doctors per department using COUNT() and AVG(), filtered with HAVING to show departments with multiple doctors.',
        'query': "SELECT dept.name AS department_name, COUNT(d.id) AS total_doctors, AVG(d.consultation_fee) AS avg_consultation_fee FROM departments dept JOIN doctors d ON dept.id = d.department_id GROUP BY dept.id, dept.name HAVING COUNT(d.id) >= 1 ORDER BY total_doctors DESC;"
    },
    {
        'id': 'view_low_stock',
        'title': '6. VIEW Query: Low Stock Pharmacy Inventory',
        'category': 'Views & Constraints',
        'explanation': 'Queries the `vw_low_stock_medicines` database view to show inventory items where stock level is below reorder thresholds.',
        'query': "SELECT * FROM vw_low_stock_medicines;"
    }
]

@sql_lab_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_query = ""
    query_result = None
    columns = []
    error_message = None
    execution_time_ms = 0
    selected_sample_id = None
    
    if request.method == 'POST':
        user_query = request.form.get('sql_query', '').strip()
        selected_sample_id = request.form.get('sample_id', '').strip()
        
        # If user picked a preset query
        if selected_sample_id:
            for s in SAMPLE_QUERIES:
                if s['id'] == selected_sample_id:
                    user_query = s['query']
                    break
                    
        # Security & Read-Only Validation
        cleaned_query = user_query.strip()
        
        # 1. Reject empty queries
        if not cleaned_query:
            error_message = "Query cannot be empty."
        # 2. Reject multiple statements (semicolons inside string literal excluded, but simple block check)
        elif ';' in cleaned_query.rstrip(';'):
            error_message = "Security Violation: Executing multiple SQL statements is strictly prohibited."
        # 3. Enforce SELECT only
        elif not re.match(r'^(SELECT|WITH)\s', cleaned_query, re.IGNORECASE):
            error_message = "Security Violation: Only safe, read-only SELECT or WITH (CTE) queries are permitted in SQL Lab."
        # 4. Blacklist dangerous SQL keywords
        elif re.search(r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|RENAME|EXEC|CALL)\b', cleaned_query, re.IGNORECASE):
            error_message = "Security Violation: DDL and DML write modifications are rejected in read-only SQL Lab."
        else:
            # Enforce row limit
            if not re.search(r'\bLIMIT\s+\d+', cleaned_query, re.IGNORECASE):
                cleaned_query = cleaned_query.rstrip(';') + " LIMIT 100"
                
            import time
            start_time = time.time()
            try:
                with get_db_cursor(dictionary=True) as cursor:
                    cursor.execute(cleaned_query)
                    query_result = cursor.fetchall()
                    if query_result and len(query_result) > 0:
                        columns = list(query_result[0].keys())
                    execution_time_ms = round((time.time() - start_time) * 1000, 2)
            except Exception as err:
                error_message = f"SQL Syntax/Execution Error: {str(err)}"
                
    return render_template('sql_lab/index.html',
                           samples=SAMPLE_QUERIES,
                           user_query=user_query,
                           query_result=query_result,
                           columns=columns,
                           error_message=error_message,
                           execution_time_ms=execution_time_ms,
                           selected_sample_id=selected_sample_id)
