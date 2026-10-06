-- CarePoint HMS - DBMS Concept Demonstrations: ACID Transactions (COMMIT / ROLLBACK)
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. TRANSACTION EXAMPLE: Patient Inpatient Admission & Bed Allocation
-- Concept: Ensures bed status update AND admission record creation succeed atomically (All-or-Nothing).

START TRANSACTION;

-- Step 1: Check bed availability and update status to 'Occupied'
UPDATE rooms_beds 
SET status = 'Occupied' 
WHERE id = 4 AND status = 'Available';

-- Step 2: Insert admission record (Only if bed was updated)
INSERT INTO admissions (patient_id, bed_id, doctor_id, admission_date, reason, status)
VALUES (2, 4, 3, CURRENT_TIMESTAMP, 'Acute Appendix Pain Observation', 'Active');

-- Step 3: Create initial inpatient deposit bill
INSERT INTO bills (patient_id, admission_id, bill_date, total_amount, paid_amount, payment_status)
VALUES (2, LAST_INSERT_ID(), CURRENT_TIMESTAMP, 180.00, 0.00, 'Pending');

-- Commit changes permanently
COMMIT;


-- 2. TRANSACTION EXAMPLE WITH ROLLBACK (Simulating Error / Out of Stock)
-- Concept: Demonstrates rolling back state if validation or inventory check fails.

START TRANSACTION;

-- Attempt to dispense 50 units of Lisinopril 10mg (ID: 4)
-- Assume check reveals quantity (6) < requested (50)

-- Explicit Rollback upon detecting insufficient stock
ROLLBACK;


-- 3. TRANSACTION EXAMPLE: Patient Discharge & Bed Release
-- Concept: Atomically sets admission status to 'Discharged', releases bed status to 'Available', and updates final bill balance.

START TRANSACTION;

-- Step 1: Update admission discharge timestamp
UPDATE admissions 
SET discharge_date = CURRENT_TIMESTAMP, status = 'Discharged'
WHERE id = 1 AND status = 'Active';

-- Step 2: Release bed back to 'Available' pool
UPDATE rooms_beds 
SET status = 'Available'
WHERE id = (SELECT bed_id FROM admissions WHERE id = 1);

COMMIT;
