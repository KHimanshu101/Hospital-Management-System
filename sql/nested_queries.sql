-- CarePoint HMS - DBMS Concept Demonstrations: Nested Queries / Subqueries
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. SCALAR SUBQUERY IN WHERE CLAUSE: Find doctors whose consultation fee is higher than average
-- Concept: Inner query returns a single scalar value (AVG consultation_fee) evaluated in outer filter.
SELECT 
    id,
    CONCAT('Dr. ', first_name, ' ', last_name) AS doctor_name,
    specialization,
    consultation_fee
FROM doctors
WHERE consultation_fee > (
    SELECT AVG(consultation_fee) 
    FROM doctors
)
ORDER BY consultation_fee DESC;


-- 2. SUBQUERY WITH IN OPERATOR: Find patients who currently have an active admission
-- Concept: Returns a set of patient_ids from `admissions` matching the IN set.
SELECT 
    id AS patient_id,
    CONCAT(first_name, ' ', last_name) AS patient_name,
    phone,
    email
FROM patients
WHERE id IN (
    SELECT DISTINCT patient_id 
    FROM admissions 
    WHERE status = 'Active'
);


-- 3. SUBQUERY WITH NOT IN OPERATOR: Find medicines that have never been prescribed
-- Concept: Identifies unused or stagnant pharmacy inventory.
SELECT 
    id AS medicine_id,
    name,
    batch_number,
    quantity,
    unit_price
FROM medicines
WHERE id NOT IN (
    SELECT DISTINCT medicine_id 
    FROM prescription_items
);


-- 4. CORRELATED SUBQUERY WITH EXISTS: Find doctors who have conducted at least one appointment today
-- Concept: Subquery relies on outer table reference (`d.id`) and evaluates per row.
SELECT 
    d.id AS doctor_id,
    CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization
FROM doctors d
WHERE EXISTS (
    SELECT 1 
    FROM appointments a 
    WHERE a.doctor_id = d.id 
      AND a.appointment_date = CURRENT_DATE
);


-- 5. SUBQUERY IN FROM CLAUSE (DERIVED TABLE): Department revenue performance summary
-- Concept: Uses subquery as a temporary virtual table with alias.
SELECT 
    dept_summary.department_name,
    dept_summary.total_doctors,
    dept_summary.avg_fee,
    dept_summary.max_fee
FROM (
    SELECT 
        dept.name AS department_name,
        COUNT(doc.id) AS total_doctors,
        AVG(doc.consultation_fee) AS avg_fee,
        MAX(doc.consultation_fee) AS max_fee
    FROM departments dept
    LEFT JOIN doctors doc ON dept.id = doc.department_id
    GROUP BY dept.id, dept.name
) AS dept_summary
WHERE dept_summary.total_doctors > 0
ORDER BY dept_summary.avg_fee DESC;
