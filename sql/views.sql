-- CarePoint HMS - DBMS Concept Demonstrations: Database Views
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. VIEW: Doctor Directory with Department Information
-- Concept: Simplifies complex JOINs into a virtual table for frontend queries.
CREATE OR REPLACE VIEW vw_doctor_details AS
SELECT 
    d.id AS doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS full_name,
    d.first_name,
    d.last_name,
    d.email,
    d.phone,
    d.specialization,
    d.consultation_fee,
    d.department_id,
    dept.name AS department_name,
    dept.code AS department_code
FROM doctors d
INNER JOIN departments dept ON d.department_id = dept.id;


-- 2. VIEW: Active Admissions and Bed Details Summary
-- Concept: Encapsulates active inpatient statuses and room locations.
CREATE OR REPLACE VIEW vw_active_admissions AS
SELECT 
    adm.id AS admission_id,
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
    TIMESTAMPDIFF(DAY, adm.admission_date, CURRENT_TIMESTAMP) AS days_admitted,
    adm.reason
FROM admissions adm
INNER JOIN patients p ON adm.patient_id = p.id
INNER JOIN rooms_beds rb ON adm.bed_id = rb.id
INNER JOIN doctors doc ON adm.doctor_id = doc.id
WHERE adm.status = 'Active';


-- 3. VIEW: Low Stock Medicines Inventory Alert
-- Concept: Filtered view providing real-time stock replenishment alerts.
CREATE OR REPLACE VIEW vw_low_stock_medicines AS
SELECT 
    id AS medicine_id,
    name,
    batch_number,
    quantity,
    reorder_level,
    unit_price,
    expiry_date,
    (reorder_level - quantity) AS units_shortage
FROM medicines
WHERE quantity <= reorder_level
ORDER BY quantity ASC;


-- 4. VIEW: Outstanding Patient Financial Balances
-- Concept: Summarizes pending/partial bills for administrative followup.
CREATE OR REPLACE VIEW vw_outstanding_bills AS
SELECT 
    b.id AS bill_id,
    b.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone AS patient_phone,
    b.bill_date,
    b.total_amount,
    b.paid_amount,
    (b.total_amount - b.paid_amount) AS balance_due,
    b.payment_status
FROM bills b
INNER JOIN patients p ON b.patient_id = p.id
WHERE b.payment_status IN ('Pending', 'Partial')
ORDER BY b.bill_date ASC;
