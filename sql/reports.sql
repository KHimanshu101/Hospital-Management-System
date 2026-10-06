-- CarePoint HMS - DBMS Analytical Reports
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. REPORT: Doctor Workload and Total Revenue Generated
SELECT 
    d.id AS doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    dept.name AS department_name,
    COUNT(DISTINCT a.id) AS total_appointments,
    COUNT(DISTINCT adm.id) AS total_admissions,
    COALESCE(SUM(bi.amount * bi.quantity), 0.00) AS total_revenue_generated
FROM doctors d
INNER JOIN departments dept ON d.department_id = dept.id
LEFT JOIN appointments a ON d.id = a.doctor_id
LEFT JOIN admissions adm ON d.id = adm.doctor_id
LEFT JOIN bills b ON adm.id = b.admission_id
LEFT JOIN bill_items bi ON b.id = bi.bill_id
GROUP BY d.id, d.first_name, d.last_name, dept.name
ORDER BY total_appointments DESC;


-- 2. REPORT: Department-wise Patient Distribution & Consultation Summary
SELECT 
    dept.id AS department_id,
    dept.name AS department_name,
    dept.code AS department_code,
    COUNT(DISTINCT doc.id) AS doctor_count,
    COUNT(DISTINCT appt.id) AS total_appointments_booked,
    SUM(CASE WHEN appt.status = 'Completed' THEN 1 ELSE 0 END) AS completed_appointments,
    SUM(CASE WHEN appt.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_appointments
FROM departments dept
LEFT JOIN doctors doc ON dept.id = doc.department_id
LEFT JOIN appointments appt ON dept.id = appt.department_id
GROUP BY dept.id, dept.name, dept.code
ORDER BY total_appointments_booked DESC;


-- 3. REPORT: Bed Occupancy & Utilization Matrix by Room Type
SELECT 
    room_type,
    COUNT(*) AS total_beds,
    SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available_beds,
    SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_beds,
    SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_beds,
    ROUND((SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS occupancy_percentage
FROM rooms_beds
GROUP BY room_type
ORDER BY occupancy_percentage DESC;


-- 4. REPORT: Monthly Revenue Breakdown and Payment Collection Efficiency
SELECT 
    DATE_FORMAT(bill_date, '%Y-%m') AS billing_month,
    COUNT(id) AS total_invoices,
    SUM(total_amount) AS gross_billed_amount,
    SUM(paid_amount) AS total_collected_amount,
    SUM(total_amount - paid_amount) AS total_outstanding_amount,
    ROUND((SUM(paid_amount) / SUM(total_amount)) * 100, 2) AS collection_rate_percentage
FROM bills
GROUP BY DATE_FORMAT(bill_date, '%Y-%m')
ORDER BY billing_month DESC;


-- 5. REPORT: Pharmacy Inventory Valuation & Reorder Status
SELECT 
    COUNT(*) AS total_medicine_items,
    SUM(quantity) AS total_units_in_stock,
    SUM(quantity * unit_price) AS total_inventory_value,
    SUM(CASE WHEN quantity <= reorder_level THEN 1 ELSE 0 END) AS items_requiring_reorder
FROM medicines;
