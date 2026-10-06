# CarePoint HMS - ER Diagram & Schema Documentation

## 1. Overview
The CarePoint Hospital Management System database (`carepoint_hms`) is designed using 3rd Normal Form (3NF) to eliminate data redundancy and preserve integrity across 12 relational tables.

## 2. Entities & Primary Keys
- **`users`** (`id` PK): User credentials and RBAC roles (`Admin`, `Receptionist`, `Doctor`).
- **`departments`** (`id` PK): Hospital departments (`Cardiology`, `Neurology`, `Orthopedics`, etc.).
- **`doctors`** (`id` PK): Medical staff linked to `departments.id` via FK.
- **`patients`** (`id` PK): Demographic records and emergency contacts.
- **`rooms_beds`** (`id` PK): Bed inventory with room numbers, bed numbers, ward types, and rates.
- **`appointments`** (`id` PK): Schedule slots with `(doctor_id, appointment_date, appointment_time)` UNIQUE constraint.
- **`admissions`** (`id` PK): Active inpatient bed allocations.
- **`bills`** (`id` PK): Patient invoices.
- **`bill_items`** (`id` PK): Itemized charges linked to `bills.id`.
- **`medicines`** (`id` PK): Pharmacy inventory with batch numbers, quantities, and prices.
- **`prescriptions`** (`id` PK): Doctor prescriptions.
- **`prescription_items`** (`id` PK): Dispensing records linked to `medicines.id`.

## 3. Key Relationships & Cardinality
1. `departments` 1 : N `doctors` (One department employs many doctors)
2. `doctors` 1 : N `appointments` (One doctor conducts many appointments)
3. `patients` 1 : N `appointments` (One patient schedules many appointments)
4. `patients` 1 : N `admissions` (One patient may have multiple admissions over time)
5. `rooms_beds` 1 : N `admissions` (One bed accommodates one active admission at a time)
6. `bills` 1 : N `bill_items` (One bill contains itemized line charges)
7. `prescriptions` 1 : N `prescription_items` (One prescription includes dispensed medicines)
