from flask import request, session, redirect

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
    return """<h2>JOWDA Owner Panel</h2>
<p>Owner access confirmed.</p>
<a href="/owner/logout">LOGOUT</a>"""
