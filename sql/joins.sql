-- CarePoint HMS - DBMS Concept Demonstrations: JOINs
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. INNER JOIN: Retrieve doctors with their assigned department details
-- Concept: Returns only rows where matching keys exist in both tables.
SELECT 
    d.id AS doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    d.consultation_fee,
    dept.name AS department_name,
    dept.code AS department_code
FROM doctors d
INNER JOIN departments dept ON d.department_id = dept.id
ORDER BY dept.name, d.last_name;


-- 2. MULTI-TABLE INNER JOIN: Detailed appointment schedules
-- Concept: Combines patients, doctors, and departments across 3 foreign keys.
SELECT 
    a.id AS appointment_id,
    a.appointment_date,
    a.appointment_time,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    p.phone AS patient_phone,
    CONCAT('Dr. ', doc.first_name, ' ', doc.last_name) AS doctor_name,
    dept.name AS department_name,
    a.reason,
    a.status
FROM appointments a
INNER JOIN patients p ON a.patient_id = p.id
INNER JOIN doctors doc ON a.doctor_id = doc.id
INNER JOIN departments dept ON a.department_id = dept.id
WHERE a.status = 'Scheduled'
ORDER BY a.appointment_date, a.appointment_time;


-- 3. LEFT JOIN: All departments and their registered doctors (including departments without doctors)
-- Concept: Preserves all rows from the left table (`departments`), inserting NULL where no doctor matches.
SELECT 
    dept.id AS department_id,
    dept.name AS department_name,
    dept.code AS department_code,
    doc.id AS doctor_id,
    CONCAT(doc.first_name, ' ', doc.last_name) AS doctor_name,
    doc.specialization
FROM departments dept
LEFT JOIN doctors doc ON dept.id = doc.department_id
ORDER BY dept.name, doc.last_name;


-- 4. LEFT JOIN WITH AGGREGATION: Total count of patients admitted per bed
-- Concept: Shows bed occupancy statistics across all beds, including unused beds (count = 0).
SELECT 
    b.id AS bed_id,
    b.room_number,
    b.bed_number,
    b.room_type,
    b.status AS current_bed_status,
    COUNT(adm.id) AS total_historical_admissions
FROM rooms_beds b
LEFT JOIN admissions adm ON b.id = adm.bed_id
GROUP BY b.id, b.room_number, b.bed_number, b.room_type, b.status
ORDER BY b.room_number, b.bed_number;


-- 5. COMPLEX 5-TABLE JOIN: Detailed Inpatient Billing Summary
-- Concept: Aggregates patient demographic, bed room rates, doctor fees, and itemized bill totals.
SELECT 
    bill.id AS bill_id,
    bill.bill_date,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    rb.room_number,
    rb.bed_number,
    rb.room_type,
    CONCAT('Dr. ', doc.first_name, ' ', doc.last_name) AS attending_doctor,
    bill.total_amount,
    bill.paid_amount,
    (bill.total_amount - bill.paid_amount) AS balance_due,
    bill.payment_status
FROM bills bill
INNER JOIN patients p ON bill.patient_id = p.id
LEFT JOIN admissions adm ON bill.admission_id = adm.id
LEFT JOIN rooms_beds rb ON adm.bed_id = rb.id
LEFT JOIN doctors doc ON adm.doctor_id = doc.id
ORDER BY bill.bill_date DESC;
