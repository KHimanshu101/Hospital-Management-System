# CarePoint HMS - 25+ Viva Examination Questions & Answers

### Q1: What is a DBMS, and why is MySQL chosen for CarePoint HMS?
**Answer:** A Database Management System (DBMS) is software that manages stored structured data efficiently and securely. MySQL 8 is chosen for CarePoint because it offers full ACID transaction compliance, InnoDB row-level locking, foreign key integrity constraints, and scalable multi-user concurrency required for hospital applications.

### Q2: Explain 1NF, 2NF, and 3NF normalization in CarePoint.
**Answer:**
- **1NF**: Ensures atomic column values (no multi-valued lists).
- **2NF**: Eliminates partial dependencies on composite keys.
- **3NF**: Eliminates transitive dependencies where non-key columns depend on other non-key columns. In CarePoint, separating Doctor details from Department details into distinct `doctors` and `departments` tables ensures 3NF compliance.

### Q3: What is the difference between Primary Key, Foreign Key, and Candidate Key?
**Answer:** A Candidate Key is any column or set of columns capable of uniquely identifying a row. A Primary Key (PK) is the chosen candidate key (e.g., `patients.id`) that uniquely identifies rows and cannot be NULL. A Foreign Key (FK) is a field referencing the primary key of another table (e.g., `doctors.department_id` -> `departments.id`) to maintain referential integrity.

### Q4: How do CHECK and UNIQUE constraints work in CarePoint?
**Answer:** UNIQUE constraints guarantee that no duplicate values exist in a column (e.g., `doctors.email` or `rooms_beds(room_number, bed_number)`). CHECK constraints enforce domain integrity rules (e.g., `consultation_fee >= 0`, `medicines.quantity >= 0`).

### Q5: What is Referential Integrity and what ON DELETE behavior is used?
**Answer:** Referential Integrity ensures child foreign keys always point to valid parent primary key records. In CarePoint, ON DELETE RESTRICT prevents accidental deletion of a department if doctors are assigned to it, while ON DELETE CASCADE automatically deletes itemized `bill_items` when a parent `bill` is removed.

### Q6: What is the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN?
**Answer:** INNER JOIN returns matching rows present in both joined tables. LEFT JOIN (LEFT OUTER JOIN) returns all rows from the left table and matching rows from the right table, inserting NULLs if no match exists. RIGHT JOIN returns all rows from the right table and matching rows from the left table.

### Q7: Explain GROUP BY and HAVING clauses with an example query.
**Answer:** GROUP BY aggregates rows sharing common column values into summary rows (e.g., grouping appointments by doctor_id). HAVING filters aggregated groups after the GROUP BY calculation occurs (e.g., HAVING COUNT(appointment_id) > 5), whereas WHERE filters individual rows before aggregation.

### Q8: What is a Correlated Subquery vs Non-correlated Subquery?
**Answer:** A Non-correlated Subquery runs independently of the outer query once and feeds its result (e.g., WHERE fee > (SELECT AVG(fee) FROM doctors)). A Correlated Subquery depends on values from the outer query row-by-row (e.g., EXISTS (SELECT 1 FROM appointments a WHERE a.doctor_id = d.id)).

### Q9: What are ACID properties in DBMS?
**Answer:** Atomicity (all-or-nothing execution), Consistency (database transitions from one valid state to another satisfying all constraints), Isolation (concurrent transactions execute independently without interference), and Durability (committed data survives system crashes).

### Q10: How does CarePoint prevent appointment schedule double-booking?
**Answer:** CarePoint enforces schedule integrity at both database and application levels. Database level: UNIQUE constraint on `(doctor_id, appointment_date, appointment_time)`. Application level: `AppointmentService.is_doctor_available()` checks existing bookings inside a transaction before inserting.

### Q11: How does bed allocation and discharge transaction work?
**Answer:** When admitting a patient, `AdmissionService.create_admission()` uses `SELECT ... FOR UPDATE` row locking to check bed availability, updates `rooms_beds.status = 'Occupied'`, and inserts an `admissions` record inside a single `START TRANSACTION ... COMMIT` block. Discharging a patient releases the bed back to 'Available' atomically.

### Q12: What is a Database Index and how does B-Tree indexing work?
**Answer:** An index is a data structure (typically a B+ Tree in MySQL InnoDB) that provides quick access paths to table rows based on indexed column values, reducing search complexity from O(N) full table scan to O(log N) tree traversal.

### Q13: Which columns in CarePoint are indexed and why?
**Answer:** Indexes are placed on foreign key columns (`department_id`, `doctor_id`, `patient_id`) to optimize JOIN lookups, and on frequently filtered attributes like `patient(last_name, first_name)`, `appointment_date`, and `medicines(quantity, reorder_level)`.

### Q14: What is a Database View and what are its advantages?
**Answer:** A View is a virtual table defined by a stored SELECT query. Advantages include: simplifying complex queries for frontends, enforcing data security by exposing only necessary columns, and decoupling application logic from underlying table restructuring.

### Q15: What is a Database Trigger? Give an example from CarePoint.
**Answer:** A Trigger is a named SQL block executed automatically in response to DML events (INSERT, UPDATE, DELETE). In CarePoint, `trg_after_dispense_deduct_stock` automatically deducts medicine inventory quantity whenever a new row is inserted into `prescription_items`.

### Q16: What is SQL Injection and how is CarePoint protected?
**Answer:** SQL Injection occurs when untrusted user input is directly concatenated into SQL query strings, allowing attackers to manipulate queries. CarePoint uses parameterized SQL queries (e.g., `cursor.execute('SELECT * FROM users WHERE username = %s', (user_input,))`) where data parameters are sent separately from query code.

### Q17: How is password security handled in CarePoint?
**Answer:** Passwords are never stored in plain text. CarePoint uses Werkzeug security helpers (`generate_password_hash` and `check_password_hash`) implementing modern salted hashing algorithms (scrypt/pbkdf2).

### Q18: How does the SQL Lab playground ensure safety against malicious queries?
**Answer:** SQL Lab restricts execution to safe SELECT queries using regex validation, rejects multiple statement chaining (`;`), blocks dangerous keywords (DROP, DELETE, UPDATE, ALTER, TRUNCATE), and enforces a maximum row limit (LIMIT 100).

### Q19: How is medicine dispensing integrated with patient billing?
**Answer:** When a prescription is dispensed in `PharmacyService`, stock availability is verified, prescription records are created, stock quantities are deducted, and line charges are automatically attached to the patient's active bill in an atomic transaction.

### Q20: How are room charges calculated for inpatient admissions?
**Answer:** Rooms have daily rates stored in `rooms_beds.daily_rate`. When discharging or billing, days admitted are calculated using `TIMESTAMPDIFF(DAY, admission_date, discharge_date)` and multiplied by the bed rate to compute itemized room charges.

### Q21: What is the difference between AUTO_INCREMENT and Oracle Sequences?
**Answer:** MySQL uses `AUTO_INCREMENT` column attributes attached directly to table primary keys to generate sequential integers. Oracle uses standalone `SEQUENCE` objects (`CREATE SEQUENCE`) queried via `NEXTVAL`.

### Q22: What are Stored Procedures vs Functions in MySQL?
**Answer:** A Stored Procedure is a compiled set of SQL statements that can perform complex business transactions and return zero or multiple result sets. A Function accepts input parameters and MUST return a single scalar value for use in expressions.

### Q23: What is Data Dictionary in a relational DBMS?
**Answer:** The Data Dictionary (e.g., `information_schema` in MySQL) is a set of read-only system tables containing metadata about the database structure, including table definitions, column types, constraints, indexes, and privileges.

### Q24: What is the difference between DELETE, TRUNCATE, and DROP?
**Answer:** DELETE is a DML statement that deletes selected rows (can be rolled back, fires triggers). TRUNCATE is a DDL statement that removes all rows quickly by resetting storage (cannot fire triggers). DROP is a DDL statement that completely removes the table schema and data from the database.

### Q25: How does CarePoint handle low stock inventory warnings?
**Answer:** Each medicine item stores a `reorder_level`. Queries and views (`vw_low_stock_medicines`) filter items where `quantity <= reorder_level`, displaying real-time warning badges on the dashboard and pharmacy module.
