# CarePoint HMS - Database Architecture & Schema Notes

## Database Design Overview
The CarePoint Hospital Management System database (`carepoint_hms`) is designed following 3rd Normal Form (3NF) principles to eliminate redundancy, ensure data integrity, and support ACID transactions.

## Relational Schema (3NF Summary)

1. **`users`**: Authentication and RBAC (Role-Based Access Control)
   - `id` (INT, PK, AUTO_INCREMENT)
   - `username` (VARCHAR(50), UNIQUE, NOT NULL)
   - `password_hash` (VARCHAR(255), NOT NULL)
   - `full_name` (VARCHAR(100), NOT NULL)
   - `role` (ENUM('Admin', 'Receptionist', 'Doctor'), NOT NULL)
   - `created_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

2. **`departments`**: Hospital departments
   - `id` (INT, PK, AUTO_INCREMENT)
   - `name` (VARCHAR(100), UNIQUE, NOT NULL)
   - `code` (VARCHAR(10), UNIQUE, NOT NULL)
   - `description` (TEXT)
   - `created_at` (DATETIME)

3. **`doctors`**: Medical staff profiles
   - `id` (INT, PK, AUTO_INCREMENT)
   - `first_name` (VARCHAR(50), NOT NULL)
   - `last_name` (VARCHAR(50), NOT NULL)
   - `email` (VARCHAR(100), UNIQUE, NOT NULL)
   - `phone` (VARCHAR(20), NOT NULL)
   - `specialization` (VARCHAR(100), NOT NULL)
   - `consultation_fee` (DECIMAL(10,2), NOT NULL, CHECK >= 0)
   - `department_id` (INT, FK -> `departments.id` ON DELETE RESTRICT)

4. **`patients`**: Demographic patient records
   - `id` (INT, PK, AUTO_INCREMENT)
   - `first_name` (VARCHAR(50), NOT NULL)
   - `last_name` (VARCHAR(50), NOT NULL)
   - `dob` (DATE, NOT NULL)
   - `gender` (ENUM('Male', 'Female', 'Other'), NOT NULL)
   - `phone` (VARCHAR(20), NOT NULL)
   - `email` (VARCHAR(100))
   - `address` (TEXT)
   - `emergency_contact` (VARCHAR(100))

5. **`rooms_beds`**: Bed inventory management
   - `id` (INT, PK, AUTO_INCREMENT)
   - `room_number` (VARCHAR(20), NOT NULL)
   - `bed_number` (VARCHAR(20), NOT NULL)
   - `room_type` (ENUM('General', 'Semi-Private', 'Private', 'ICU'), NOT NULL)
   - `daily_rate` (DECIMAL(10,2), NOT NULL, CHECK >= 0)
   - `status` (ENUM('Available', 'Occupied', 'Maintenance'), DEFAULT 'Available')
   - UNIQUE constraint on (`room_number`, `bed_number`)

6. **`appointments`**: Patient-Doctor scheduling
   - `id` (INT, PK, AUTO_INCREMENT)
   - `patient_id` (INT, FK -> `patients.id` ON DELETE RESTRICT)
   - `doctor_id` (INT, FK -> `doctors.id` ON DELETE RESTRICT)
   - `department_id` (INT, FK -> `departments.id` ON DELETE RESTRICT)
   - `appointment_date` (DATE, NOT NULL)
   - `appointment_time` (TIME, NOT NULL)
   - `reason` (TEXT)
   - `status` (ENUM('Scheduled', 'Completed', 'Cancelled', 'No-Show'), DEFAULT 'Scheduled')

7. **`admissions`**: Inpatient care tracking
   - `id` (INT, PK, AUTO_INCREMENT)
   - `patient_id` (INT, FK -> `patients.id`)
   - `bed_id` (INT, FK -> `rooms_beds.id`)
   - `doctor_id` (INT, FK -> `doctors.id`)
   - `admission_date` (DATETIME, NOT NULL)
   - `discharge_date` (DATETIME, NULLABLE)
   - `reason` (TEXT)
   - `status` (ENUM('Active', 'Discharged'), DEFAULT 'Active')

8. **`bills`**: Billing invoices
   - `id` (INT, PK, AUTO_INCREMENT)
   - `patient_id` (INT, FK -> `patients.id`)
   - `admission_id` (INT, NULLABLE, FK -> `admissions.id`)
   - `bill_date` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
   - `total_amount` (DECIMAL(10,2), DEFAULT 0.00)
   - `paid_amount` (DECIMAL(10,2), DEFAULT 0.00)
   - `payment_status` (ENUM('Pending', 'Paid', 'Partial'), DEFAULT 'Pending')

9. **`bill_items`**: Itemized charges
   - `id` (INT, PK, AUTO_INCREMENT)
   - `bill_id` (INT, FK -> `bills.id` ON DELETE CASCADE)
   - `description` (VARCHAR(255), NOT NULL)
   - `amount` (DECIMAL(10,2), NOT NULL)
   - `quantity` (INT, DEFAULT 1)
   - `item_type` (ENUM('Room Charge', 'Doctor Fee', 'Medicine', 'Procedure', 'Misc'))

10. **`medicines`**: Pharmacy inventory
    - `id` (INT, PK, AUTO_INCREMENT)
    - `name` (VARCHAR(100), NOT NULL)
    - `batch_number` (VARCHAR(50), NOT NULL)
    - `quantity` (INT, NOT NULL, CHECK >= 0)
    - `expiry_date` (DATE, NOT NULL)
    - `unit_price` (DECIMAL(10,2), NOT NULL, CHECK >= 0)
    - `reorder_level` (INT, DEFAULT 10)

11. **`prescriptions`**: Doctor prescriptions
    - `id` (INT, PK, AUTO_INCREMENT)
    - `appointment_id` (INT, NULLABLE, FK -> `appointments.id`)
    - `patient_id` (INT, FK -> `patients.id`)
    - `doctor_id` (INT, FK -> `doctors.id`)
    - `prescription_date` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
    - `notes` (TEXT)

12. **`prescription_items`**: Dispensing records
    - `id` (INT, PK, AUTO_INCREMENT)
    - `prescription_id` (INT, FK -> `prescriptions.id` ON DELETE CASCADE)
    - `medicine_id` (INT, FK -> `medicines.id`)
    - `quantity` (INT, NOT NULL, CHECK > 0)
    - `dosage` (VARCHAR(100))
    - `unit_price` (DECIMAL(10,2), NOT NULL)
    - `total_price` (DECIMAL(10,2), NOT NULL)
