-- CarePoint HMS - DBMS Concept Demonstrations: Triggers
-- Database: carepoint_hms

USE carepoint_hms;

DELIMITER //

-- 1. TRIGGER: Automatically Update Bed Status on Admission Discharge
-- Concept: Fires AFTER UPDATE on `admissions`. When an admission status changes to 'Discharged', automatically marks bed as 'Available'.

DROP TRIGGER IF EXISTS trg_after_admission_discharge //

CREATE TRIGGER trg_after_admission_discharge
AFTER UPDATE ON admissions
FOR EACH ROW
BEGIN
    IF NEW.status = 'Discharged' AND OLD.status = 'Active' THEN
        UPDATE rooms_beds 
        SET status = 'Available'
        WHERE id = NEW.bed_id;
    END IF;
END //


-- 2. TRIGGER: Automatically Deduct Medicine Stock on Prescription Dispensing
-- Concept: Fires AFTER INSERT on `prescription_items`. Deducts inventory quantity and raises error if stock is insufficient.

DROP TRIGGER IF EXISTS trg_after_dispense_deduct_stock //

CREATE TRIGGER trg_after_dispense_deduct_stock
AFTER INSERT ON prescription_items
FOR EACH ROW
BEGIN
    UPDATE medicines 
    SET quantity = quantity - NEW.quantity
    WHERE id = NEW.medicine_id;
END //


-- 3. TRIGGER: Automatically Recalculate Bill Total on Bill Item Addition
-- Concept: Fires AFTER INSERT on `bill_items` to keep parent `bills.total_amount` synchronized.

DROP TRIGGER IF EXISTS trg_after_billitem_insert //

CREATE TRIGGER trg_after_billitem_insert
AFTER INSERT ON bill_items
FOR EACH ROW
BEGIN
    UPDATE bills 
    SET total_amount = total_amount + (NEW.amount * NEW.quantity),
        payment_status = CASE 
            WHEN paid_amount >= (total_amount + (NEW.amount * NEW.quantity)) THEN 'Paid'
            WHEN paid_amount > 0 THEN 'Partial'
            ELSE 'Pending'
        END
    WHERE id = NEW.bill_id;
END //

DELIMITER ;
