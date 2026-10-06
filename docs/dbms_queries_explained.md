# CarePoint HMS - Educational DBMS Query Guide

## 1. DDL (Data Definition Language)
DDL statements define the database structure.
```sql
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    consultation_fee DECIMAL(10,2) CHECK (consultation_fee >= 0),
    department_id INT NOT NULL,
    CONSTRAINT fk_doctor_department FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

## 2. DML (Data Manipulation Language)
DML statements manipulate stored data.
```sql
INSERT INTO patients (first_name, last_name, dob, gender, phone) 
VALUES ('John', 'Doe', '1990-01-01', 'Male', '555-0199');

UPDATE rooms_beds SET status = 'Occupied' WHERE id = 1;

DELETE FROM patients WHERE id = 10;
```

## 3. JOIN Operations
JOINs combine rows from two or more tables based on related columns.
```sql
-- INNER JOIN
SELECT d.first_name, dept.name 
FROM doctors d 
INNER JOIN departments dept ON d.department_id = dept.id;

-- LEFT JOIN
SELECT dept.name, COUNT(d.id) AS total_doctors 
FROM departments dept 
LEFT JOIN doctors d ON dept.id = d.department_id 
GROUP BY dept.id, dept.name;
```

## 4. Subqueries / Nested Queries
Subqueries nest one SELECT statement inside another.
```sql
-- Scalar Subquery
SELECT name, consultation_fee 
FROM doctors 
WHERE consultation_fee > (SELECT AVG(consultation_fee) FROM doctors);

-- IN Subquery
SELECT * FROM patients 
WHERE id IN (SELECT patient_id FROM admissions WHERE status = 'Active');
```

## 5. Database Views
```sql
CREATE VIEW vw_low_stock_medicines AS
SELECT id, name, batch_number, quantity, reorder_level 
FROM medicines 
WHERE quantity <= reorder_level;
```

## 6. ACID Transactions
```sql
START TRANSACTION;
UPDATE rooms_beds SET status = 'Occupied' WHERE id = 2;
INSERT INTO admissions (patient_id, bed_id, doctor_id, admission_date) VALUES (1, 2, 1, NOW());
COMMIT;
```
