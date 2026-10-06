-- CarePoint HMS - DBMS Concept Demonstrations: Indexes & Integrity Constraints
-- Database: carepoint_hms

USE carepoint_hms;

-- 1. PRIMARY KEY & UNIQUE CONSTRAINTS EXPLANATION
-- Primary Keys enforce Entity Integrity (Not Null + Unique).
-- Unique constraints prevent duplicate data entries for unique identifiers like Email or Room+Bed combinations.

-- Example DDL showing UNIQUE & CHECK constraints
/*
ALTER TABLE doctors ADD CONSTRAINT uk_doctor_email UNIQUE (email);
ALTER TABLE doctors ADD CONSTRAINT chk_doctor_fee CHECK (consultation_fee >= 0);
ALTER TABLE rooms_beds ADD CONSTRAINT uk_room_bed UNIQUE (room_number, bed_number);
*/

-- 2. SECONDARY INDEX CREATION
-- Concept: Indexes speed up query execution (SELECT / WHERE / JOIN) at the cost of slight INSERT/UPDATE overhead.

-- Index on patient name search (frequently queried in live search controls)
CREATE INDEX idx_patients_search ON patients (last_name, first_name);

-- Index on appointment search filters (doctor_id, date, status)
CREATE INDEX idx_appointments_filter ON appointments (doctor_id, appointment_date, status);

-- Index on inventory stock checking
CREATE INDEX idx_medicines_reorder ON medicines (quantity, reorder_level);

-- 3. INSPECTING INDEXES IN MYSQL
SHOW INDEX FROM patients;
SHOW INDEX FROM appointments;
SHOW INDEX FROM doctors;

-- 4. EXPLAIN QUERY PLAN DEMONSTRATION
-- Concept: Demonstrates how MySQL Query Optimizer utilizes indexes for execution.
EXPLAIN SELECT * FROM appointments 
WHERE doctor_id = 1 AND appointment_date = CURRENT_DATE;
