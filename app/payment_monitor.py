import os
import requests

TRON_API_KEY = os.getenv("TRON_PRO_API_KEY")
TRON_API_URL = "https://api.trongrid.io"
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def check_api_ready():
    return True

def get_transactions(address):
    url = f"{TRON_API_URL}/v1/accounts/{address}/transactions/trc20"
    headers = {}
    if TRON_API_KEY:
        headers["TRON-PRO-API-KEY"] = TRON_API_KEY

    params = {
        "limit": 20,
        "contract_address": USDT_CONTRACT
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_usdt_transfers(address):
    data = get_transactions(address)
    transfers = []

    for item in data.get("data", []):
        if item.get("token_info", {}).get("address") != USDT_CONTRACT:
            continue

        transfers.append({
            "tx_hash": item.get("transaction_id"),
            "from_address": item.get("from"),
            "to_address": item.get("to"),
            "amount": int(item.get("value", 0)) / 1_000_000,
            "token": "USDT",
            "network": "TRC20",
            "timestamp": item.get("block_timestamp")
        })

    return transfers

if __name__ == "__main__":
    address = os.getenv("JOWDA_PAYMENT_WALLET")
    if not address:
        print("JOWDA_PAYMENT_WALLET_MISSING")
    else:
        transfers = get_usdt_transfers(address)
        print("USDT_TRANSFERS", len(transfers))

def save_unmatched_transfers(transfers):
    from database import DB_PATH
    import sqlite3
    from datetime import datetime

    conn = sqlite3.connect(DB_PATH)

    for item in transfers:
        tx_hash = item["tx_hash"]

        exists = conn.execute(
            "SELECT 1 FROM payments WHERE tx_hash = ?",
            (tx_hash,)
        ).fetchone()

        if exists:
            continue

        conn.execute(
            """INSERT INTO payments
               (invoice_id, tx_hash, from_address, to_address, amount,
                token, network, detected_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                None,
                tx_hash,
                item["from_address"],
                item["to_address"],
                item["amount"],
                item["token"],
                item["network"],
                datetime.utcnow().isoformat(),
                "UNMATCHED"
            )
        )

    conn.commit()
    conn.close()

def match_transfers_to_invoices(transfers):
    from database import DB_PATH
    import sqlite3

    conn = sqlite3.connect(DB_PATH)

    for item in transfers:
        if item["to_address"] != os.getenv("JOWDA_PAYMENT_WALLET"):
            continue

        rows = conn.execute(
            """SELECT id, invoice_number, amount
               FROM invoices
               WHERE status = 'PENDING' AND amount = ?""",
            (item["amount"],)
        ).fetchall()

        if len(rows) != 1:
            continue

        invoice_id = rows[0][0]
        tx_hash = item["tx_hash"]

        exists = conn.execute(
            "SELECT 1 FROM payments WHERE tx_hash = ?",
            (tx_hash,)
        ).fetchone()

        if exists:
            continue

        conn.execute(
            """INSERT INTO payments
               (invoice_id, tx_hash, from_address, to_address, amount,
                token, network, detected_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                invoice_id,
                tx_hash,
                item["from_address"],
                item["to_address"],
                item["amount"],
                item["token"],
                item["network"],
                __import__("datetime").datetime.utcnow().isoformat(),
                "MATCHED"
            )
        )

        conn.execute(
            "UPDATE invoices SET status = 'PAID' WHERE id = ?",
            (invoice_id,)
        )

    conn.commit()
    conn.close()

def generate_unique_payment_amount(base_amount):
    from database import DB_PATH
    import sqlite3

    conn = sqlite3.connect(DB_PATH)

    for cents in range(1, 100):
        payment_amount = round(float(base_amount) + (cents / 100), 2)

        exists = conn.execute(
            "SELECT 1 FROM invoices WHERE status = 'PENDING' AND payment_amount = ?",
            (payment_amount,)
        ).fetchone()

        if not exists:
            conn.close()
            return payment_amount

    conn.close()
    raise RuntimeError("No unique payment amount available")

def create_invoice_qr(invoice_number, base_url):
    import qrcode
    from pathlib import Path

    url = f"{base_url}/invoice/{invoice_number}"
    output = Path(__file__).parent / "static" / f"invoice_{invoice_number}.png"

    img = qrcode.make(url)
    img.save(output)

    return str(output)
