import pytest

def calculate_invoice_status(total_amount, paid_amount):
    total = float(total_amount)
    paid = float(paid_amount)
    if paid >= total and total > 0:
        return 'Paid'
    elif paid > 0:
        return 'Partial'
    return 'Pending'

def is_low_stock(quantity, reorder_level):
    return int(quantity) <= int(reorder_level)

def test_invoice_status_logic():
    assert calculate_invoice_status(100.00, 0.00) == 'Pending'
    assert calculate_invoice_status(100.00, 40.00) == 'Partial'
    assert calculate_invoice_status(100.00, 100.00) == 'Paid'
    assert calculate_invoice_status(100.00, 150.00) == 'Paid'

def test_low_stock_logic():
    assert is_low_stock(5, 10) is True
    assert is_low_stock(10, 10) is True
    assert is_low_stock(15, 10) is False
