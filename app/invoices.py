from database import init_db, get_connection
from datetime import datetime
from psycopg2.extras import RealDictCursor

def create_invoice(invoice_number, customer_name, amount, wallet_address, due_date=None, business_name=None):
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO invoices (invoice_number, customer_name, business_name, amount, token, network, wallet_address, due_date, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (invoice_number, customer_name, business_name, amount, "USDT", "TRC20", wallet_address, due_date, datetime.utcnow().isoformat())
    )
    conn.commit()
    cur.close()
    conn.close()

def get_invoice(invoice_number):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM invoices WHERE invoice_number = %s",
        (invoice_number,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def record_payment(invoice_id, tx_hash, from_address, to_address, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (invoice_id, tx_hash, from_address, to_address, amount, token, network, detected_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (invoice_id, tx_hash, from_address, to_address, amount, "USDT", "TRC20", datetime.utcnow().isoformat())
    )
    conn.commit()
    cur.close()
    conn.close()

def reconcile_invoice(invoice_number):
    invoice = get_invoice(invoice_number)
    if not invoice:
        return "NOT_FOUND"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id = %s AND status = 'UNMATCHED'",
        (invoice["id"],)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    paid_amount = row[0]

    if paid_amount == invoice["amount"]:
        return "PAID"
    if paid_amount < invoice["amount"]:
        return "UNDERPAID"
    return "OVERPAID"

def record_unmatched_payment(tx_hash, from_address, to_address, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (invoice_id, tx_hash, from_address, to_address, amount, token, network, detected_at, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (None, tx_hash, from_address, to_address, amount, "USDT", "TRC20", datetime.utcnow().isoformat(), "UNMATCHED")
    )
    conn.commit()
    cur.close()
    conn.close()

def update_invoice_status(invoice_number):
    status = reconcile_invoice(invoice_number)
    if status == "NOT_FOUND":
        return status

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE invoices SET status = %s WHERE invoice_number = %s",
        (status, invoice_number)
    )
    conn.commit()
    cur.close()
    conn.close()
    return status
