import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "stablecoin_invoice.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            amount REAL NOT NULL,
            token TEXT NOT NULL,
            network TEXT NOT NULL,
            wallet_address TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT "PENDING",
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER, tx_hash TEXT UNIQUE NOT NULL, from_address TEXT, to_address TEXT, amount REAL NOT NULL, token TEXT NOT NULL, network TEXT NOT NULL, detected_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'UNMATCHED')""")
    conn.commit()
    conn.close()
