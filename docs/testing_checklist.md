# CarePoint HMS - Testing & Evaluation Checklist

Use this checklist to systematically verify and demonstrate feature functionality during project evaluation.

## 1. Authentication & Security
- [ ] Log in with `admin` / `admin123` & verify redirect to Dashboard.
- [ ] Log out & verify protected routes redirect back to `/login`.
- [ ] Attempt SQL injection in login input & verify sanitization.

## 2. Patient & Doctor Management
- [ ] Add a new patient in `/patients/add` & verify insertion in directory table.
- [ ] Edit patient details & verify database update.
- [ ] Filter doctors by department in `/doctors` dropdown.

## 3. Scheduling & Collision Prevention
- [ ] Schedule an appointment for Dr. Smith at Date `X` and Time `09:00`.
- [ ] Attempt to book a second appointment for Dr. Smith at the same Date `X` and Time `09:00`.
- [ ] Verify red error alert: *"Conflict detected: Doctor already has a scheduled appointment at this exact date and time slot."*

## 4. Inpatient Admissions & Bed Allocation
- [ ] Select an available bed (e.g. Room R101 Bed B2) and admit a patient.
- [ ] Verify bed status changes to `Occupied` in `/beds`.
- [ ] Click `Discharge` on the admission record & verify bed status changes back to `Available`.

## 5. Pharmacy Inventory & Dispensing
- [ ] View inventory list & check low-stock warning badges.
- [ ] Dispense 5 units of Paracetamol for a patient.
- [ ] Verify stock quantity decreases by 5 and medicine charge is appended to invoice.

## 6. SQL Playground & Safety
- [ ] Select preset query "1. INNER JOIN: Doctors with Department Names" & click Run.
- [ ] Verify results render in HTML table.
- [ ] Type `DROP TABLE users;` & click Run.
- [ ] Verify security rejection banner.
