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
    from database import get_connection
    from datetime import datetime

    conn = get_connection()
    cur = conn.cursor()

    for item in transfers:
        tx_hash = item["tx_hash"]

        cur.execute(
            "SELECT 1 FROM payments WHERE tx_hash = %s",
            (tx_hash,)
        )

        exists = cur.fetchone()

        if exists:
            continue

        cur.execute(
            """INSERT INTO payments
               (invoice_id, tx_hash, from_address, to_address, amount,
                token, network, detected_at, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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
    cur.close()
    conn.close()

def match_transfers_to_invoices(transfers):
    from database import get_connection

    conn = get_connection()
    cur = conn.cursor()

    for item in transfers:
        if item["to_address"] != os.getenv("JOWDA_PAYMENT_WALLET"):
            continue

        cur.execute(
            """SELECT id, invoice_number, amount
               FROM invoices
               WHERE status = 'PENDING' AND amount = %s""",
            (item["amount"],)
        )

        rows = cur.fetchall()

        if len(rows) != 1:
            continue

        invoice_id = rows[0][0]
        tx_hash = item["tx_hash"]

        cur.execute(
            "SELECT 1 FROM payments WHERE tx_hash = %s",
            (tx_hash,)
        )

        exists = cur.fetchone()

        if exists:
            continue

        cur.execute(
            """INSERT INTO payments
               (invoice_id, tx_hash, from_address, to_address, amount,
                token, network, detected_at, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
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

        cur.execute(
            "UPDATE invoices SET status = 'PAID' WHERE id = %s",
            (invoice_id,)
        )

    conn.commit()
    conn.close()

def create_invoice_qr(invoice_number, base_url):
    import qrcode
    from pathlib import Path

    url = f"{base_url}/invoice/{invoice_number}"
    output = Path(__file__).parent / "static" / f"invoice_{invoice_number}.png"

    img = qrcode.make(url)
    img.save(output)

    return str(output)
