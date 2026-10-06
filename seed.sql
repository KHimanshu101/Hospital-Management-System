-- CarePoint Hospital Management System - Fictional Seed Data
USE carepoint_hms;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE password_resets;
TRUNCATE TABLE prescription_items;
TRUNCATE TABLE prescriptions;
TRUNCATE TABLE bill_items;
TRUNCATE TABLE bills;
TRUNCATE TABLE admissions;
TRUNCATE TABLE appointments;
TRUNCATE TABLE medicines;
TRUNCATE TABLE rooms_beds;
TRUNCATE TABLE patients;
TRUNCATE TABLE doctors;
TRUNCATE TABLE departments;
TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. Demo Users (Including Unique Emails for Recovery)
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@carepoint.org', 'scrypt:32768:8:1$AqHOo3SH30altrSU$2a5e6d0414f8b626c47286f70f22ed0aeb24cf41d2f4b9e657e8c6e0f2d5a55b43d361e03e32d6fa59edc297e3490316c9d02b816502f5aedd97f48627ce9d16', 'System Administrator', 'Admin'),
('receptionist', 'receptionist@carepoint.org', 'scrypt:32768:8:1$OMum5tDgAAXojulY$5498204b87af418c455b8e4398c99f9c1ee5af498727cf81f7823983cab7debbe97489a499c0fa1cf194d132f13963583b8bf03337c73e32f0d03af361f622d4', 'Sarah Jenkins', 'Receptionist'),
('dr_smith', 'dr_smith@carepoint.org', 'scrypt:32768:8:1$0B12oHIFWBHcKErY$51b0f8e1c5d6ae1b2a16a2246bec205472a7a7c5da9ed14b9cb5fd20dd870690b4ce577a5a5895269ca974f1e258978478476ee925166ba562095af19c30f0a8', 'Dr. Robert Smith', 'Doctor');

-- 2. Departments
INSERT INTO departments (id, name, code, description) VALUES
(1, 'Cardiology', 'CARD', 'Heart and cardiovascular system medical care'),
(2, 'Neurology', 'NEUR', 'Brain, spinal cord, and nervous system disorders'),
(3, 'Orthopedics', 'ORTH', 'Musculoskeletal system, joints, and bones care'),
(4, 'Pediatrics', 'PEDI', 'Infant, child, and adolescent medical care'),
(5, 'Emergency', 'EMER', '24/7 Acute critical care and trauma intervention');

-- 3. Doctors
INSERT INTO doctors (id, first_name, last_name, email, phone, specialization, consultation_fee, department_id) VALUES
(1, 'Robert', 'Smith', 'r.smith@carepoint.org', '555-0101', 'Interventional Cardiology', 120.00, 1),
(2, 'Elena', 'Rostova', 'e.rostova@carepoint.org', '555-0102', 'Clinical Neurophysiology', 150.00, 2),
(3, 'Marcus', 'Vance', 'm.vance@carepoint.org', '555-0103', 'Orthopedic Surgery', 140.00, 3),
(4, 'Aisha', 'Khan', 'a.khan@carepoint.org', '555-0104', 'Pediatric Cardiology', 110.00, 4),
(5, 'David', 'Miller', 'd.miller@carepoint.org', '555-0105', 'Trauma & Emergency', 90.00, 5),
(6, 'Grace', 'Hopper', 'g.hopper@carepoint.org', '555-0106', 'General Neurology', 130.00, 2);

-- 4. Patients
INSERT INTO patients (id, first_name, last_name, dob, gender, phone, email, address, emergency_contact) VALUES
(1, 'Alice', 'Johnson', '1985-04-12', 'Female', '555-0201', 'alice.j@example.com', '123 Maple Street, Cityville', 'Bob Johnson (Spouse): 555-0299'),
(2, 'Brian', 'Miller', '1992-08-25', 'Male', '555-0202', 'bmiller@example.com', '456 Oak Avenue, Metroville', 'Clara Miller (Mother): 555-0298'),
(3, 'Catherine', 'Davis', '1978-11-03', 'Female', '555-0203', 'cdavis@example.com', '789 Pine Road, Suburbia', 'Dan Davis (Husband): 555-0297'),
(4, 'Daniel', 'Wilson', '2001-01-19', 'Male', '555-0204', 'dwilson@example.com', '321 Elm Lane, Downtown', 'Eva Wilson (Sister): 555-0296'),
(5, 'Emily', 'Brown', '1995-06-30', 'Female', '555-0205', 'ebrown@example.com', '654 Birch Court, Uptown', 'Frank Brown (Father): 555-0295'),
(6, 'Frank', 'Thomas', '1960-09-14', 'Male', '555-0206', 'fthomas@example.com', '987 Cedar Boulevard, Cityville', 'Grace Thomas (Wife): 555-0294'),
(7, 'Georgia', 'Taylor', '2010-03-22', 'Female', '555-0207', 'gtaylor@example.com', '159 Walnut Street, Suburbia', 'Henry Taylor (Father): 555-0293'),
(8, 'Harold', 'White', '1952-12-05', 'Male', '555-0208', 'hwhite@example.com', '753 Spruce Drive, Metroville', 'Irene White (Daughter): 555-0292');

-- 5. Rooms and Beds
INSERT INTO rooms_beds (id, room_number, bed_number, room_type, daily_rate, status) VALUES
(1, 'R101', 'B1', 'General', 100.00, 'Occupied'),
(2, 'R101', 'B2', 'General', 100.00, 'Available'),
(3, 'R102', 'B1', 'Semi-Private', 180.00, 'Occupied'),
(4, 'R102', 'B2', 'Semi-Private', 180.00, 'Available'),
(5, 'R201', 'B1', 'Private', 300.00, 'Available'),
(6, 'R202', 'B1', 'Private', 300.00, 'Maintenance'),
(7, 'ICU-1', 'B1', 'ICU', 650.00, 'Occupied'),
(8, 'ICU-1', 'B2', 'ICU', 650.00, 'Available'),
(9, 'ICU-2', 'B1', 'ICU', 650.00, 'Available'),
(10, 'R301', 'B1', 'General', 100.00, 'Available');

-- 6. Appointments
INSERT INTO appointments (id, patient_id, doctor_id, department_id, appointment_date, appointment_time, reason, status) VALUES
(1, 1, 1, 1, CURRENT_DATE, '09:00:00', 'Routine Cardiac Follow-up & ECG', 'Scheduled'),
(2, 2, 2, 2, CURRENT_DATE, '10:30:00', 'Migraine and Dizziness Assessment', 'Scheduled'),
(3, 3, 3, 3, CURRENT_DATE, '14:00:00', 'Knee Joint Pain Evaluation', 'Scheduled'),
(4, 4, 4, 4, DATE_ADD(CURRENT_DATE, INTERVAL 1 DAY), '11:00:00', 'Pediatric Asthma Checkup', 'Scheduled'),
(5, 5, 5, 5, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '16:00:00', 'Acute Allergic Reaction', 'Completed'),
(6, 6, 1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), '09:30:00', 'Hypertension Consultation', 'Completed'),
(7, 7, 4, 4, DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), '15:00:00', 'Seasonal Fever & Cough', 'Completed'),
(8, 8, 6, 2, DATE_ADD(CURRENT_DATE, INTERVAL 2 DAY), '13:30:00', 'Neuropathy Follow-up', 'Scheduled');

-- 7. Inpatient Admissions
INSERT INTO admissions (id, patient_id, bed_id, doctor_id, admission_date, discharge_date, reason, status) VALUES
(1, 6, 1, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), NULL, 'Post-myocardial infarction observation', 'Active'),
(2, 3, 3, 3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), NULL, 'Elective Knee Arthroscopy Recovery', 'Active'),
(3, 8, 7, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), NULL, 'Acute Stroke Monitoring in ICU', 'Active'),
(4, 1, 2, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 10 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 7 DAY), 'Transient Ischemic Attack Management', 'Discharged');

-- 8. Bills
INSERT INTO bills (id, patient_id, admission_id, bill_date, total_amount, paid_amount, payment_status) VALUES
(1, 6, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), 420.00, 100.00, 'Partial'),
(2, 3, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 500.00, 0.00, 'Pending'),
(3, 8, 3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), 2750.00, 2750.00, 'Paid'),
(4, 1, 4, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 7 DAY), 680.00, 680.00, 'Paid');

-- 9. Bill Items
INSERT INTO bill_items (id, bill_id, description, amount, quantity, item_type) VALUES
(1, 1, 'General Room Charge (3 days)', 100.00, 3, 'Room Charge'),
(2, 1, 'Cardiology Doctor Fee', 120.00, 1, 'Doctor Fee'),
(3, 2, 'Semi-Private Room Deposit', 180.00, 2, 'Room Charge'),
(4, 2, 'Orthopedic Surgery Fee', 140.00, 1, 'Doctor Fee'),
(5, 3, 'ICU Room Charge (4 days)', 650.00, 4, 'Room Charge'),
(6, 3, 'Neurology Specialist Consultation', 150.00, 1, 'Doctor Fee'),
(7, 4, 'Outpatient Diagnostic & Pharmacy Charge', 680.00, 1, 'Misc');

-- 10. Medicines Inventory
INSERT INTO medicines (id, name, batch_number, quantity, expiry_date, unit_price, reorder_level) VALUES
(1, 'Amoxicillin 500mg', 'AMX-2025-01', 150, '2027-06-30', 12.50, 20),
(2, 'Atorvastatin 20mg', 'ATV-2025-09', 85, '2026-12-31', 24.00, 15),
(3, 'Metformin 850mg', 'MET-2025-04', 200, '2027-03-15', 8.00, 30),
(4, 'Lisinopril 10mg', 'LIS-2025-08', 6, '2026-11-20', 15.00, 15),
(5, 'Paracetamol 500mg', 'PAR-2025-12', 500, '2028-01-01', 2.50, 50),
(6, 'Ibuprofen 400mg', 'IBU-2025-03', 4, '2026-10-15', 4.50, 20),
(7, 'Ciprofloxacin 500mg', 'CIP-2025-07', 45, '2027-08-31', 18.00, 10);

-- 11. Prescriptions
INSERT INTO prescriptions (id, appointment_id, patient_id, doctor_id, prescription_date, notes) VALUES
(1, 5, 5, 5, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 'Take Paracetamol after meals. Rest for 3 days.'),
(2, 6, 6, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 'Atorvastatin once daily before sleep. Monitor BP weekly.');

-- 12. Prescription Items
INSERT INTO prescription_items (id, prescription_id, medicine_id, quantity, dosage, unit_price, total_price) VALUES
(1, 1, 5, 10, '1 tablet every 8 hours', 2.50, 25.00),
(2, 2, 2, 30, '1 tablet daily at bedtime', 24.00, 720.00);
