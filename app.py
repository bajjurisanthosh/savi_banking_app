from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from functools import wraps
from datetime import date
import mock_data as db

app = Flask(__name__)
app.secret_key = "boa-demo-secret-key-2024"


@app.context_processor
def inject_notifications():
    email = session.get("user_email")
    if email and email in db.NOTIFICATIONS:
        notifs = db.NOTIFICATIONS[email]
        return {"notification_count": len(notifs), "notifications": notifs}
    return {"notification_count": 0, "notifications": []}


# ── Auth helper ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            flash("Please sign in to access your account.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Alert helper ─────────────────────────────────────────────────────────────

def _check_alerts(user_email, txn):
    if user_email not in db.ALERTS:
        return
    notifs = db.NOTIFICATIONS.setdefault(user_email, [])
    for alert in db.ALERTS[user_email]:
        if not alert["active"]:
            continue
        if alert["account_id"] != "all" and alert["account_id"] != txn["account_id"]:
            continue
        if abs(txn["amount"]) > alert["threshold"]:
            notifs.append({
                "id": f"ntf{len(notifs):03d}",
                "txn_id": txn["id"],
                "message": f"Alert: ${abs(txn['amount']):,.2f} transaction at \"{txn['description']}\" exceeded your ${alert['threshold']:,.2f} threshold.",
                "amount": txn["amount"],
                "date": txn["date"],
                "read": False,
            })


# ── Public routes ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db.USERS.get(email)
        if user and user["password"] == password:
            session["user_email"] = email
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name'].split()[0]}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if email in db.USERS:
            flash("An account with that email already exists.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        else:
            # Register new demo user (in-memory only)
            db.USERS[email] = {"password": password, "name": name, "member_since": str(date.today().year)}
            session["user_email"] = email
            session["user_name"] = name
            flash(f"Account created! Welcome, {name.split()[0]}.", "success")
            return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You've been signed out.", "info")
    return redirect(url_for("index"))


# ── Protected routes ─────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    recent = [t for t in db.TRANSACTIONS if t["account_id"] == "chk001"][:5]
    return render_template(
        "dashboard.html",
        accounts=db.ACCOUNTS,
        recent_transactions=recent,
        user_name=session["user_name"],
    )


@app.route("/transactions")
@login_required
def transactions():
    account_filter = request.args.get("account", "all")
    category_filter = request.args.get("category", "all")

    txns = db.TRANSACTIONS[:]
    if account_filter != "all":
        txns = [t for t in txns if t["account_id"] == account_filter]
    if category_filter != "all":
        txns = [t for t in txns if t["category"] == category_filter]

    # Sort newest first
    txns.sort(key=lambda t: t["date"], reverse=True)

    return render_template(
        "transactions.html",
        transactions=txns,
        accounts=db.ACCOUNTS,
        categories=db.CATEGORIES,
        account_filter=account_filter,
        category_filter=category_filter,
    )


@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        from_acct = request.form.get("from_account")
        to_payee = request.form.get("to_payee", "").strip()
        amount_str = request.form.get("amount", "0")
        transfer_date = request.form.get("transfer_date") or date.today().isoformat()
        memo = request.form.get("memo", "").strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Please enter a valid amount greater than $0.", "error")
            return render_template("transfer.html", accounts=db.ACCOUNTS)

        # Find source account and check balance
        acct = next((a for a in db.ACCOUNTS if a["id"] == from_acct), None)
        if not acct:
            flash("Invalid source account.", "error")
            return render_template("transfer.html", accounts=db.ACCOUNTS)

        description = f"Transfer to {to_payee}" if to_payee else "Transfer"
        if memo:
            description += f" — {memo}"

        # Append transaction
        db.TRANSACTIONS.insert(0, {
            "id": f"txn{len(db.TRANSACTIONS):03d}",
            "date": transfer_date,
            "description": description,
            "amount": -round(amount, 2),
            "category": "Transfer",
            "account_id": from_acct,
        })
        _check_alerts(session["user_email"], db.TRANSACTIONS[0])

        # Update balance
        acct["balance"] = round(acct["balance"] - amount, 2)
        acct["available"] = round(acct["available"] - amount, 2)

        flash(f"Transfer of ${amount:,.2f} to {to_payee or 'payee'} was successful!", "success")
        return redirect(url_for("transfer"))

    return render_template("transfer.html", accounts=db.ACCOUNTS)


@app.route("/alerts", methods=["GET", "POST"])
@login_required
def alerts():
    email = session["user_email"]
    db.ALERTS.setdefault(email, [])
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            threshold = float(request.form.get("threshold", 0))
            account_id = request.form.get("account_id", "all")
            if threshold > 0:
                rules = db.ALERTS[email]
                rules.append({"id": f"alr{len(rules):03d}", "threshold": threshold, "account_id": account_id, "active": True})
                flash(f"Alert created for transactions over ${threshold:,.2f}.", "success")
        elif action == "delete":
            alert_id = request.form.get("alert_id")
            db.ALERTS[email] = [a for a in db.ALERTS[email] if a["id"] != alert_id]
            flash("Alert removed.", "info")
        elif action == "toggle":
            alert_id = request.form.get("alert_id")
            for a in db.ALERTS[email]:
                if a["id"] == alert_id:
                    a["active"] = not a["active"]
        return redirect(url_for("alerts"))
    return render_template("alerts.html", alerts=db.ALERTS[email], accounts=db.ACCOUNTS, user_name=session["user_name"])


@app.route("/notifications/dismiss/<ntf_id>", methods=["POST"])
@login_required
def dismiss_notification(ntf_id):
    email = session["user_email"]
    db.NOTIFICATIONS[email] = [n for n in db.NOTIFICATIONS.get(email, []) if n["id"] != ntf_id]
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/notifications/dismiss-all", methods=["POST"])
@login_required
def dismiss_all_notifications():
    db.NOTIFICATIONS[session["user_email"]] = []
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
