from datetime import datetime
import sqlite3
from database import init_db, DB_PATH

def create_invoice(invoice_number, customer_name, amount, wallet_address, due_date=None, business_name=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO invoices (invoice_number, customer_name, business_name, amount, token, network, wallet_address, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (invoice_number, customer_name, business_name, amount, "USDT", "TRC20", wallet_address, due_date, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_invoice(invoice_number):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM invoices WHERE invoice_number = ?",
        (invoice_number,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def record_payment(invoice_id, tx_hash, from_address, to_address, amount):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO payments (invoice_id, tx_hash, from_address, to_address, amount, token, network, detected_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (invoice_id, tx_hash, from_address, to_address, amount, "USDT", "TRC20", datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def reconcile_invoice(invoice_number):
    invoice = get_invoice(invoice_number)
    if not invoice:
        return "NOT_FOUND"

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id = ? AND status = 'UNMATCHED'",
        (invoice["id"],)
    ).fetchone()
    conn.close()

    paid_amount = row[0]

    if paid_amount == invoice["amount"]:
        return "PAID"
    if paid_amount < invoice["amount"]:
        return "UNDERPAID"
    return "OVERPAID"

def record_unmatched_payment(tx_hash, from_address, to_address, amount):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO payments (invoice_id, tx_hash, from_address, to_address, amount, token, network, detected_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (None, tx_hash, from_address, to_address, amount, "USDT", "TRC20", datetime.utcnow().isoformat(), "UNMATCHED")
    )
    conn.commit()
    conn.close()

def update_invoice_status(invoice_number):
    status = reconcile_invoice(invoice_number)
    if status == "NOT_FOUND":
        return status

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE invoices SET status = ? WHERE invoice_number = ?",
        (status, invoice_number)
    )
    conn.commit()
    conn.close()
    return status
