from flask import request, session, redirect
from database import get_connection

OWNER_USERNAME = "mohammedalajem"
OWNER_PASSWORD = __import__("os").environ.get("JOWDA_OWNER_PASSWORD")

def owner_login():
    if request.method == "POST":
        if not OWNER_PASSWORD or request.form.get("username") != OWNER_USERNAME or request.form.get("password") != OWNER_PASSWORD:
            return "Invalid password", 401
        session["owner_logged_in"] = True
        return redirect("/owner")
    return """<h2>JOWDA Owner Login</h2>
<form method="post">
<input type="text" name="username" required autocomplete="username">
<input type="password" name="password" required autocomplete="current-password">
<button type="submit">LOGIN</button>
</form>"""

def owner_logout():
    session.pop("owner_logged_in", None)
    return redirect("/owner/login")

def owner_required():
    return session.get("owner_logged_in") is True


def owner_dashboard():
    if not owner_required():
        return redirect("/owner/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM invoices")
    total_invoices = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM payments")
    total_payments = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices")
    total_invoice_amount = cur.fetchone()[0]

    cur.execute("SELECT status, COUNT(*) FROM invoices GROUP BY status ORDER BY status")
    statuses = cur.fetchall()

    cur.close()
    conn.close()

    status_html = "".join(
        f"<li>{status}: {count}</li>" for status, count in statuses
    )

    return f"""<h2>JOWDA Owner Panel</h2>
<p><strong>Total Invoices:</strong> {total_invoices}</p>
<p><strong>Total Payments:</strong> {total_payments}</p>
<p><strong>Total Invoice Amount:</strong> {total_invoice_amount} USDT</p>
<h3>Invoice Status</h3>
<ul>{status_html}</ul>
<a href="/owner/logout">LOGOUT</a>"""
