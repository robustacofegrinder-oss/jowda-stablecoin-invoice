from flask import Flask, request, redirect, session, send_file
import os
from pathlib import Path
import requests
from datetime import datetime
import secrets
from invoices import create_invoice, get_invoice
from payment_monitor import create_invoice_qr
from config import PAYMENT_WALLET_ADDRESS

app = Flask(__name__)
app.secret_key = 'jowda-session-key'

@app.route("/googleb51f2905fbbd3099.html")
def google_verification():
    return send_file(str(Path(__file__).resolve().parent.parent / "googleb51f2905fbbd3099.html"))

def generate_invoice_number():
    return "JOWDA-" + datetime.now().strftime("%Y%m%d") + "-" + secrets.token_hex(2).upper()

def tron_base58_to_hex(address):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    num = 0
    for char in address:
        num = num * 58 + alphabet.index(char)

    raw = num.to_bytes((num.bit_length() + 7) // 8, "big")
    pad = len(address) - len(address.lstrip("1"))
    raw = b"\x00" * pad + raw

    payload = raw[:-4]
    return payload.hex().lower()[2:]


@app.route("/sitemap.xml")
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://jowda-stablecoin-invoice.onrender.com/</loc></url>
<url><loc>https://jowda-stablecoin-invoice.onrender.com/plans</loc></url>
<url><loc>https://jowda-stablecoin-invoice.onrender.com/create-invoice</loc></url>
</urlset>""", 200, {"Content-Type": "application/xml"}

@app.route("/")
def home():
    return """
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>JOWDA — Smart Invoicing</title>
    <style>
    *{box-sizing:border-box}
    body{margin:0;background:#eef3fb;font-family:Arial,sans-serif;color:#172033;padding:28px 15px}
    .home{text-align:center;max-width:820px;margin:auto}
    .brand{font-size:38px;font-weight:700;color:#1746a2}
    .tag{font-size:13px;color:#71809a;margin-top:6px}
    .preview{max-width:700px;margin:28px auto 0;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 15px 45px rgba(23,70,162,.14);text-align:left}
    .preview-row{display:flex;align-items:center;justify-content:center;gap:28px;margin-top:28px}.jowda-image{width:220px;max-width:30%;height:auto;border-radius:16px;box-shadow:0 15px 45px rgba(23,70,162,.14)}
    @media(max-width:900px){.preview-row{flex-direction:column}.jowda-image{max-width:280px;width:70%}}
    .top{background:#1746a2;color:#fff;padding:24px 30px;display:flex;justify-content:space-between;gap:20px}
    .invoice-brand{font-size:24px;font-weight:700}
    .small{font-size:11px;opacity:.8;margin-top:5px}
    .inv-title{text-align:right;font-size:22px;font-weight:700}
    .body{padding:28px 30px}
    .meta{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:22px}
    .label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#71809a;margin-bottom:5px}
    .value{font-size:14px;font-weight:600}
    .amount-box{background:#f5f8ff;border:1px solid #dce6f7;border-radius:10px;padding:17px;margin-bottom:20px}
    .amount-label{font-size:10px;color:#71809a;text-transform:uppercase;letter-spacing:1px}
    .amount{font-size:28px;color:#1746a2;font-weight:700;margin-top:4px}
    .section{font-size:13px;font-weight:700;color:#1746a2;margin:18px 0 9px;border-bottom:2px solid #e8eef8;padding-bottom:7px}
    .payment{border:1px solid #e0e7f2;border-radius:9px;padding:13px}
    .row{padding:7px 0;display:flex;justify-content:space-between;gap:15px;border-bottom:1px solid #edf1f7;font-size:12px}
    .row:last-child{border-bottom:0}
    .key{color:#71809a}
    .val{font-weight:600;text-align:right}
    .total{display:flex;justify-content:space-between;margin-top:20px;padding-top:16px;border-top:2px solid #1746a2;font-weight:700}
    .footer{text-align:center;padding:17px;background:#fafcff;color:#71809a;font-size:11px}
    .protection{max-width:700px;margin:22px auto 0;padding:22px 25px;background:#fff;border:1px solid #dce6f7;border-radius:14px;box-shadow:0 8px 25px rgba(23,70,162,.08);text-align:left}
    .trust-line{max-width:700px;margin:18px auto 0;text-align:center;font-size:15px;font-weight:700;letter-spacing:1.2px;color:#1746a2}
    .benefits{max-width:700px;margin:28px auto 0;padding:24px 25px;background:#fff;border:1px solid #dce6f7;border-radius:14px;box-shadow:0 8px 25px rgba(23,70,162,.08)}
    .benefits-title{text-align:center;font-size:20px;font-weight:700;color:#1746a2;margin-bottom:17px}
    .benefits-grid{display:grid;grid-template-columns:1fr 1fr;gap:11px 25px;text-align:left;font-size:13px;color:#34415a}
    .pricing{max-width:700px;margin:28px auto 0;text-align:center}
    @media(max-width:600px){.benefits-grid{grid-template-columns:1fr}}
    .pricing-title{font-size:20px;font-weight:700;color:#172033;margin-bottom:15px}
    .plans{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .plan{background:#fff;border:1px solid #dce6f7;border-radius:13px;padding:20px 12px;box-shadow:0 7px 22px rgba(23,70,162,.07)}
    .plan.featured{border:2px solid #1746a2}
    .plan-name{font-size:11px;font-weight:700;letter-spacing:1px;color:#71809a}
    .plan-price{font-size:25px;font-weight:700;color:#1746a2;margin-top:9px}
    .plan-price span{font-size:12px}
    .plan-note{font-size:11px;color:#71809a;margin-top:5px}
    @media(max-width:600px){.plans{grid-template-columns:1fr}}
    .protection-title{text-align:center;font-size:18px;font-weight:700;color:#1746a2}
    .protection-subtitle{text-align:center;margin-top:5px;font-size:12px;color:#71809a}
    .features{display:grid;grid-template-columns:1fr 1fr;gap:10px 25px;margin-top:17px}
    .feature{font-size:13px;color:#34415a}
    .feature span{color:#1746a2;font-weight:700;margin-right:7px}
    @media(max-width:600px){.features{grid-template-columns:1fr}}
    @media(max-width:600px){.top{padding:20px;flex-direction:column}.inv-title{text-align:left}.body{padding:22px 20px}.meta{grid-template-columns:1fr}.brand{font-size:32px}}
    </style>
    </head>
    <body>
    <div class="home">
      <div class="brand">JOWDA</div>
      <div class="tag">NO LIMITS TO TRUST</div>
      <div class="tag">Smart Invoicing &amp; Payment Reconciliation</div>
      <div class="preview-row">
        <div class="preview">
        <div class="top">
          <div><div class="invoice-brand">JOWDA</div><div class="small">NO LIMITS TO TRUST</div><div class="small">Smart Invoicing &amp; Payment Reconciliation</div></div>
          <div><div class="inv-title">SAMPLE INVOICE</div><div class="small">#JOWDA-001</div></div>
        </div>
        <div class="body">
          <div class="meta">
            <div><div class="label">Bill To</div><div class="value">Your Customer</div></div>
            <div><div class="label">Issue Date</div><div class="value">2026-09-29</div></div>
            <div><div class="label">Due Date</div><div class="value">—</div></div>
            <div><div class="label">Status</div><div class="value">PENDING</div></div>
          </div>
          <div class="amount-box"><div class="amount-label">Amount Due</div><div class="amount">25,000 USDT</div></div>
          <div class="section">Payment Details</div>
          <div class="payment">
            <div class="row"><span class="key">Token</span><span class="val">USDT</span></div>
            <div class="row"><span class="key">Network</span><span class="val">TRC-20</span></div>
            <div class="row"><span class="key">Wallet Address</span><span class="val">Payment Wallet</span></div>
          </div>
          <div class="total"><span>Total Due</span><span>25,000 USDT</span></div>
        </div>
        <div class="footer"><strong>USDT — TRC20</strong><br>Thank you for your business.</div>
        </div>
        <img class="jowda-image" src="/static/jowda_image.jpg" alt="JOWDA">
      </div>
      <div class="protection">
        <div class="protection-title">Payment Protection</div>
        <div class="protection-subtitle">Built-in controls for safer payment reconciliation</div>
        <div class="features">
          <div class="feature"><span>✓</span> Duplicate transaction detection</div>
          <div class="feature"><span>✓</span> Underpayment detection</div>
          <div class="feature"><span>✓</span> Overpayment detection</div>
          <div class="feature"><span>✓</span> Automatic payment reconciliation</div>
        </div>
      </div>
      <div class="trust-line">YOUR TRANSFERS. ALWAYS ACCOUNTED FOR.</div>
      <div class="pricing">
        <div class="pricing-title">Simple, Transparent Pricing</div>
        <div class="plans">
          <div class="plan"><div class="plan-name">MONTHLY</div><div class="plan-price">50 <span>USDT</span></div><div class="plan-note">30 days</div></div>
          <div class="plan"><div class="plan-name">3 MONTHS</div><div class="plan-price">120 <span>USDT</span></div><div class="plan-note">90 days</div></div>
          <div class="plan featured"><div class="plan-name">YEARLY</div><div class="plan-price">250 <span>USDT</span></div><div class="plan-note">365 days</div></div>
        </div>
      </div>
      <div class="benefits">
        <div class="benefits-title">What You Get</div>
        <div class="benefits-grid">
          <div>✓ Professional Invoice Creation</div>
          <div>✓ USDT / TRC20 Payment Support</div>
          <div>✓ Payment Reconciliation</div>
          <div>✓ Duplicate Transaction Protection</div>
          <div>✓ Underpayment &amp; Overpayment Detection</div>
          <div>✓ Invoice Status Tracking</div>
          <div>✓ QR Code Payment Support</div>
          <div>✓ Print / Save Invoice as PDF</div>
        </div>
        <div style="text-align:center;margin-top:28px;"><a href="/checkout" style="display:inline-block;background:#2563eb;color:#fff;padding:14px 28px;border-radius:10px;text-decoration:none;font-weight:700;letter-spacing:.4px;">CREATE YOUR INVOICE</a></div>
        <div style="text-align:center;margin-top:28px;padding-bottom:10px;color:#53657d;font-size:14px;">Contact: <a href="mailto:JOWDATEC@gmail.com" style="color:#1746a2;font-weight:700;text-decoration:none;">JOWDATEC@gmail.com</a></div>
      </div>
    </div>
    </body>
    </html>
    """
@app.route("/invoice/<invoice_number>")
def invoice_page(invoice_number):
    invoice = get_invoice(invoice_number)
    if not invoice:
        return "Invoice not found", 404
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Invoice {{invoice["invoice_number"]}} — JOWDA</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#eef3fb;font-family:Arial,sans-serif;color:#172033;padding:35px 15px;display:flex;justify-content:center;align-items:center;min-height:100vh}} .invoice{{max-width:780px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 15px 45px rgba(23,70,162,.14)}} .top{{background:#1746a2;color:#fff;padding:30px 38px;display:flex;justify-content:space-between;gap:20px}} .brand{{font-size:27px;font-weight:700}} .tag{{font-size:12px;opacity:.8;margin-top:6px}} .inv-title{{text-align:right;font-size:25px;font-weight:700}} .inv-no{{font-size:14px;margin-top:7px;opacity:.9}} .body{{padding:35px 38px}} .meta{{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-bottom:30px}} .label{{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#71809a;margin-bottom:7px}} .value{{font-size:16px;font-weight:600}} .amount-box{{background:#f5f8ff;border:1px solid #dce6f7;border-radius:12px;padding:22px;margin-bottom:28px}} .amount-label{{font-size:12px;color:#71809a;text-transform:uppercase;letter-spacing:1px}} .amount{{font-size:28px;color:#1746a2;font-weight:700;margin-top:5px}} .section{{font-size:15px;font-weight:700;color:#1746a2;margin:25px 0 10px;border-bottom:2px solid #e8eef8;padding-bottom:9px}} .payment{{border:1px solid #e0e7f2;border-radius:10px;padding:18px}} .pay-row{{padding:9px 0;display:flex;justify-content:space-between;gap:15px;border-bottom:1px solid #edf1f7}} .pay-row:last-child{{border-bottom:0}} .pay-key{{color:#71809a}} .pay-value{{font-weight:600;text-align:right;word-break:break-all}} .status{{display:inline-block;padding:7px 13px;border-radius:20px;background:#eef4ff;color:#1746a2;font-size:13px;font-weight:700}} .total{{display:flex;justify-content:space-between;align-items:center;margin-top:25px;padding-top:20px;border-top:2px solid #1746a2;font-size:18px;font-weight:700}} .total span:last-child{{font-size:25px;color:#1746a2}} .footer{{text-align:center;padding:22px 30px;background:#fafcff;color:#71809a;font-size:12px}} .print{{display:block;margin:22px auto 0;background:#1746a2;color:#fff;border:0;border-radius:8px;padding:11px 22px;font-weight:700;cursor:pointer}} @media(max-width:600px){{.top{{padding:24px;flex-direction:column}}.inv-title{{text-align:left}}.body{{padding:25px 22px}}.meta{{grid-template-columns:1fr}}.amount{{font-size:30px}}}} @media print{{@page{{size:A4;margin:10mm}}body{{background:#fff;padding:0;display:block;min-height:0}}.invoice{{box-shadow:none;width:100%;max-width:780px;margin:0 auto}}.top{{padding:18px 25px;background:#1746a2 !important;color:#fff !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}.body{{padding:12px 22px}}.meta{{gap:10px;margin-bottom:10px}}.amount-box{{padding:9px;margin-bottom:10px}}.section{{margin:10px 0 5px;padding-bottom:4px}}.payment{{padding:7px}}.pay-row{{padding:3px 0}}.total{{margin-top:8px;padding-top:7px}}.footer{{display:none}}.print{{display:none}}}}
</style>
</head>
<body>
<div class="invoice">
<div class="top"><div><div class="brand">JOWDA</div><div class="tag">NO LIMITS TO TRUST</div><div class="tag">Smart Invoicing &amp; Payment Reconciliation</div></div><div><div class="inv-title">INVOICE</div><div class="inv-no">#{{invoice["invoice_number"]}}</div></div></div>
<div class="body">
<div class="meta"><div><div class="label">Bill To</div><div class="value">{{invoice["customer_name"]}}</div><div style="margin-top:7px;font-size:14px;color:#53657d">{{invoice["business_name"] or "—"}}</div></div><div><div class="label">Issue Date</div><div class="value">{{invoice["created_at"][:10]}}</div></div><div><div class="label">Due Date</div><div class="value">{{invoice["due_date"] or "—"}}</div></div><div><div class="label">Status</div><div class="status">{{invoice["status"]}}</div></div></div>
<div class="amount-box"><div class="amount-label">Amount Due</div><div class="amount">{{invoice["amount"]}} {{invoice["token"]}}</div></div>
<div class="section">Payment Details</div><div style="text-align:center;margin:10px 0"><img src="/static/wallet_qr.png" alt="USDT TRC20 Payment QR" style="width:180px;height:180px;border:1px solid #e0e7f2;border-radius:10px;padding:8px;background:#fff"><div style="margin-top:10px;color:#71809a;font-size:12px">Scan to pay with USDT on TRC20</div></div><div class="payment"><div class="pay-row"><span class="pay-key">Token</span><span class="pay-value">{{invoice["token"]}}</span></div><div class="pay-row"><span class="pay-key">Network</span><span class="pay-value">{{invoice["network"]}}</span></div><div class="pay-row"><span class="pay-key">Wallet Address</span><span class="pay-value">{{invoice["wallet_address"]}}</span></div></div>
<div class="total"><span>Total Due</span><span>{invoice["amount"]} {invoice["token"]}</span></div><div style="text-align:center;margin-top:10px;font-size:13px;color:#53657d">Thank you for your business.</div>
<button class="print" onclick="window.print()">Print / Save PDF</button>
</div><div class="footer"><strong>USDT — TRC20</strong><br>Thank you for your business.</div>
</div>
</body>
</html>
"""

def payment_result(title, message, success=False):
    color = "#16845b" if success else "#c23b3b"
    icon = "✓" if success else "!"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JOWDA — Payment Result</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f7fb;font-family:Arial,sans-serif;color:#24344d;display:flex;align-items:center;justify-content:center;min-height:100vh;padding:20px}}
.card{{width:100%;max-width:520px;background:#fff;border-radius:16px;padding:42px 32px;box-shadow:0 12px 35px rgba(31,55,88,.10);text-align:center}}
.brand{{font-size:30px;font-weight:800;color:#1769d1;letter-spacing:1px}}
.tag{{font-size:12px;color:#71809a;margin-top:5px}}
.icon{{width:58px;height:58px;border-radius:50%;background:{color};color:#fff;font-size:34px;line-height:58px;margin:28px auto 18px;font-weight:700}}
h1{{font-size:24px;margin:0 0 12px;color:{color}}}
.message{{font-size:15px;line-height:1.7;color:#53657d}}
.footer{{margin-top:28px;font-size:12px;color:#8a97a8}}
</style>
</head>
<body>
<div class="card">
<div class="brand">JOWDA</div>
<div class="tag">NO LIMITS TO TRUST</div>
<div class="icon">{icon}</div>
<h1>{title}</h1>
<div class="message">{message}</div>
<div class="footer">Smart Invoicing &amp; Payment Reconciliation</div>
</div>
</body>
</html>"""

@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    tx_hash = request.form.get("tx_hash", "").strip()

    invoice_number = session.get("invoice_number")
    if not invoice_number:
        return redirect("/checkout")

    invoice = get_invoice(invoice_number)
    if not invoice:
        return "Invoice not found", 404

    if invoice["status"] == "PAID":
        return payment_result("Already Paid", "This invoice has already been paid.", True)

    if not tx_hash or len(tx_hash) != 64:
        return payment_result("Invalid TX Hash", "Please check the transaction hash and try again.")

    from database import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM payments WHERE tx_hash = %s",
        (tx_hash,)
    )
    used = cur.fetchone()
    cur.close()
    conn.close()

    if used:
        return payment_result("TX Hash Already Used", "This transaction hash has already been submitted.")

    api_url = f"https://api.trongrid.io/v1/transactions/{tx_hash}/events"
    headers = {}
    api_key = os.getenv("TRON_PRO_API_KEY")
    if api_key:
        headers["TRON-PRO-API-KEY"] = api_key

    try:
        response = requests.get(
            api_url,
            headers=headers,
            params={"only_confirmed": "true"},
            timeout=10
        )
        response.raise_for_status()
        events = response.json().get("data", [])
    except Exception:
        return payment_result("Verification Unavailable", "Unable to verify the transaction right now. Please try again.")

    expected_amount = float(invoice["amount"])
    expected_wallet = tron_base58_to_hex(PAYMENT_WALLET_ADDRESS)
    expected_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

    matched = None

    for event in events:
        if event.get("transaction_id") != tx_hash:
            continue
        if event.get("event_name") != "Transfer":
            continue
        if event.get("contract_address") != expected_contract:
            continue

        result = event.get("result", {})
        from_address = result.get("from")
        to_address = result.get("to")
        raw_value = result.get("value")

        if (to_address or "").lower() != expected_wallet:
            continue

        try:
            amount = int(raw_value) / 1_000_000
        except (TypeError, ValueError):
            continue

        if amount != expected_amount:
            continue

        block_timestamp = event.get("block_timestamp")
        if not block_timestamp:
            continue

        try:
            invoice_timestamp = datetime.fromisoformat(invoice["created_at"]).timestamp()
            if block_timestamp / 1000 < invoice_timestamp:
                continue
        except (TypeError, ValueError):
            continue

        matched = (from_address, to_address, amount)
        break

    if not matched:
        return payment_result("Payment Not Found", "The transaction does not match this invoice. Please check the amount, token, network, and destination.")

    from_address, to_address, amount = matched

    from database import get_connection
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO payments
           (invoice_id, tx_hash, from_address, to_address, amount,
            token, network, detected_at, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            invoice["id"],
            tx_hash,
            from_address,
            to_address,
            amount,
            "USDT",
            "TRC20",
            datetime.utcnow().isoformat(),
            "MATCHED"
        )
    )
    cur.execute(
        "UPDATE invoices SET status = 'PAID', tx_hash = %s WHERE id = %s",
        (tx_hash, invoice["id"])
    )
    conn.commit()
    cur.close()
    conn.close()

    return payment_result("Payment Verified", f"Invoice {invoice_number} is now PAID.", True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
@app.route("/create-invoice", methods=["GET", "POST"])
def create_invoice_page():
    if request.method == "POST":
        create_invoice(request.form["invoice_number"], request.form["customer_name"], float(request.form["amount"]), PAYMENT_WALLET_ADDRESS or request.form["wallet_address"], request.form.get("due_date") or None)
        return redirect("/")
    return "<h1>Create Invoice</h1><form method=post>Invoice Number: <input name=invoice_number required><br>Customer Name: <input name=customer_name required><br>Amount USDT: <input name=amount type=number step=0.01 required><br>Wallet Address: <input name=wallet_address required><br>Due Date: <input name=due_date type=date><br><button type=submit>Create Invoice</button></form>"

@app.route("/plans")
def plans():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JOWDA — Choose Your Plan</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,sans-serif;background:linear-gradient(135deg,#071a35,#123d68,#0b6b78);color:#fff;min-height:100vh}
.container{max-width:1050px;margin:auto;padding:55px 20px}
.brand{text-align:center;font-size:34px;font-weight:800;letter-spacing:4px}
.tag{text-align:center;color:#b9d9e8;letter-spacing:3px;font-size:13px;margin-top:8px}
h1{text-align:center;font-size:42px;margin:55px 0 12px}
.subtitle{text-align:center;color:#d7e8ef;font-size:17px;max-width:650px;margin:0 auto 42px;line-height:1.6}
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.card{background:rgba(255,255,255,.96);color:#10263b;border-radius:18px;padding:30px 24px;text-align:center;box-shadow:0 14px 35px rgba(0,0,0,.22)}
.card h2{margin:0 0 18px;font-size:22px}
.price{font-size:34px;font-weight:800;margin:10px 0}
.duration{color:#61717d;margin-bottom:28px}
.btn{display:block;text-decoration:none;background:#0b6b78;color:#fff;padding:14px;border-radius:10px;font-weight:700;letter-spacing:.5px}
.btn:hover{background:#084f5a}
.note{text-align:center;margin-top:38px;color:#cce1e8;font-size:14px}
@media(max-width:750px){.plans{grid-template-columns:1fr}.container{padding-top:35px}h1{font-size:34px}}
</style>
</head>
<body>
<div class="container">
<div class="brand">JOWDA</div>
<div class="tag">NO LIMITS TO TRUST</div>
<h1>Choose Your Plan</h1>
<p class="subtitle">Simple, transparent plans designed to help you manage your invoices and payments with confidence.</p>
<div class="plans">
<div class="card"><h2>MONTHLY</h2><div class="price">50 USDT</div><div class="duration">30 days</div><a class="btn" href="/payment/monthly">PAY NOW</a></div>
<div class="card"><h2>3 MONTHS</h2><div class="price">120 USDT</div><div class="duration">90 days</div><a class="btn" href="/payment/3months">PAY NOW</a></div>
<div class="card"><h2>YEARLY</h2><div class="price">250 USDT</div><div class="duration">365 days</div><a class="btn" href="/payment/yearly">PAY NOW</a></div>
</div>
<p class="note">Secure payment with USDT on the TRC20 network.</p>
</div>
</body>
</html>"""
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        session.pop("invoice_number", None)
        session["customer_name"] = request.form["customer_name"].strip()
        session["business_name"] = request.form["business_name"].strip()
        return redirect("/plans")

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JOWDA — Customer Details</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,sans-serif;background:linear-gradient(135deg,#071a35,#123d68,#0b6b78);color:#fff;min-height:100vh}
.container{max-width:620px;margin:auto;padding:55px 20px}
.brand{text-align:center;font-size:34px;font-weight:800;letter-spacing:4px}
.tag{text-align:center;color:#b9d9e8;letter-spacing:3px;font-size:13px;margin-top:8px}
.card{background:rgba(255,255,255,.97);color:#10263b;border-radius:20px;padding:35px 25px;margin-top:45px;box-shadow:0 16px 40px rgba(0,0,0,.25)}
h1{text-align:center;margin:0 0 10px;font-size:30px}
.subtitle{text-align:center;color:#61717d;margin-bottom:28px}
label{display:block;font-size:14px;font-weight:700;margin:18px 0 8px}
input{width:100%;padding:14px;border:1px solid #cbd8de;border-radius:9px;font-size:16px}
button{width:100%;margin-top:25px;border:0;background:#0b6b78;color:#fff;padding:14px;border-radius:10px;font-weight:700;font-size:16px;cursor:pointer}
</style>
</head>
<body>
<div class="container">
<div class="brand">JOWDA</div>
<div class="tag">NO LIMITS TO TRUST</div>
<div class="card">
<h1>Customer Details</h1>
<p class="subtitle">Please enter your name and business or company name.</p>
<form method="post">
<label>FULL NAME</label>
<input type="text" name="customer_name" required maxlength="100" autocomplete="name">
<label>BUSINESS / COMPANY NAME</label>
<input type="text" name="business_name" required maxlength="120">
<button type="submit">CONTINUE TO PLANS</button>
</form>
</div>
</div>
</body>
</html>"""

@app.route("/payment/<plan>")
def payment(plan):
    plans = {
        "monthly": ("MONTHLY", "50 USDT", "30 days"),
        "3months": ("3 MONTHS", "120 USDT", "90 days"),
        "yearly": ("YEARLY", "250 USDT", "365 days")
    }
    if plan not in plans:
        return "Invalid plan", 404
    name, price, duration = plans[plan]

    if "customer_name" not in session or "business_name" not in session:
        return redirect("/checkout")

    if "invoice_number" not in session:
        try:
            print("PAYMENT_DEBUG: start invoice creation", flush=True)
            invoice_number = generate_invoice_number()
            print(f"PAYMENT_DEBUG: invoice_number={invoice_number}", flush=True)
            create_invoice(
                invoice_number,
                session["customer_name"],
                float(price.split()[0]),
                PAYMENT_WALLET_ADDRESS,
                None,
                session["business_name"]
            )
            print("PAYMENT_DEBUG: create_invoice OK", flush=True)
            session["invoice_number"] = invoice_number
            create_invoice_qr(invoice_number, request.host_url.rstrip("/"))
            print("PAYMENT_DEBUG: create_invoice_qr OK", flush=True)
        except Exception:
            import traceback
            print("PAYMENT_DEBUG: ERROR", flush=True)
            traceback.print_exc()
            raise

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JOWDA — Payment</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:Arial,sans-serif;background:linear-gradient(135deg,#071a35,#123d68,#0b6b78);color:#fff;min-height:100vh}}
.container{{max-width:720px;margin:auto;padding:55px 20px}}
.brand{{text-align:center;font-size:34px;font-weight:800;letter-spacing:4px}}
.tag{{text-align:center;color:#b9d9e8;letter-spacing:3px;font-size:13px;margin-top:8px}}
.card{{background:rgba(255,255,255,.97);color:#10263b;border-radius:20px;padding:35px 25px;margin-top:45px;text-align:center;box-shadow:0 16px 40px rgba(0,0,0,.25)}}
h1{{margin:0 0 10px;font-size:32px}}
.subtitle{{color:#61717d;margin-bottom:28px}}
.info{{display:grid;gap:12px;margin:25px 0}}
.row{{background:#eef5f7;border-radius:10px;padding:14px}}
.label{{display:block;color:#60727d;font-size:13px;margin-bottom:5px}}
.value{{font-weight:700;font-size:18px}}
.address{{word-break:break-all;font-size:15px}}
.qr{{width:190px;height:190px;object-fit:contain;margin:20px auto;display:block}}
.note{{color:#61717d;font-size:14px;line-height:1.6}}
.btn{{display:inline-block;margin-top:20px;text-decoration:none;background:#0b6b78;color:#fff;padding:14px 28px;border-radius:10px;font-weight:700}}
</style>
</head>
<body>
<div class="container">
<div class="brand">JOWDA</div>
<div class="tag">NO LIMITS TO TRUST</div>
<div class="card">
<h1>Complete Your Payment</h1>
<p class="subtitle">You selected the {name} plan.</p>
<p style="text-align:center;margin:18px 0;color:#53657d;font-size:14px;">INVOICE #{session["invoice_number"]} · <a href="/invoice/{session["invoice_number"]}" style="color:#1746a2;font-weight:700;text-decoration:none;">VIEW INVOICE</a></p>
<div class="info">
<div class="row"><span class="label">PLAN</span><span class="value">{name}</span></div>
<div class="row"><span class="label">AMOUNT</span><span class="value">{price}</span></div>
<div class="row"><span class="label">DURATION</span><span class="value">{duration}</span></div>
<div class="row"><span class="label">NETWORK</span><span class="value">USDT — TRC20</span></div>
<div class="row"><span class="label">PAYMENT ADDRESS</span><span class="value address" id="wallet">{PAYMENT_WALLET_ADDRESS}</span><div><button type="button" onclick="navigator.clipboard.writeText(document.getElementById('wallet').innerText);this.innerText='COPIED ✓'" style="margin-top:14px;padding:10px 18px;border:0;border-radius:8px;background:#0b6b78;color:#fff;font-weight:700;cursor:pointer">COPY ADDRESS</button></div></div>
</div>
<img class="qr" src="/static/wallet_qr.png" alt="JOWDA Payment QR">
<p class="note">Send the exact amount shown above to the payment address using the TRC20 network.</p>
<form method="post" action="/verify-payment" style="margin-top:22px;">
<label for="tx_hash" style="display:block;text-align:left;font-weight:700;color:#53657d;margin-bottom:8px;">TX HASH</label>
<input id="tx_hash" name="tx_hash" type="text" placeholder="Paste your transaction hash" required style="width:100%;box-sizing:border-box;padding:13px;border:1px solid #ccd6e2;border-radius:8px;font-size:14px;">
<button type="submit" class="btn" style="border:0;margin-top:12px;width:100%;">VERIFY PAYMENT</button>
</form>
<a class="btn" href="/plans">BACK TO PLANS</a>
</div>
</div>
</body>
</html>"""
