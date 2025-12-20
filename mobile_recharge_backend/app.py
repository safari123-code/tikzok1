import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = "secret-key-123"

DB_PATH = os.path.join("database", "app.db")


# ======================
# DB HELPERS
# ======================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("database", exist_ok=True)
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ======================
# ROOT
# ======================
@app.get("/")
def root():
    return redirect(url_for("dashboard"))


# ======================
# AUTH
# ======================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Email et mot de passe obligatoires.", "danger")
            return redirect(url_for("register"))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, generate_password_hash(password)),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Email déjà utilisé.", "warning")
            return redirect(url_for("register"))
        finally:
            db.close()

        flash("Compte créé ✅. Connecte-toi.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            flash("Connexion réussie ✅", "success")
            return redirect(url_for("account_home"))

        flash("Email ou mot de passe incorrect.", "danger")
        return redirect(url_for("login"))

    return render_template("auth/login.html")


@app.get("/logout")
def logout():
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for("login"))


# ======================
# LOGIN CHECK
# ======================
def require_login():
    return "user_id" in session


# ======================
# HOME
# ======================
@app.get("/dashboard")
def dashboard():
    return render_template("home/dashboard.html")


@app.get("/history")
def history():
    return render_template("home/history.html")


# ======================
# INBOX
# ======================
@app.get("/inbox")
def inbox():
    return render_template("inbox/inbox.html")


# ======================
# ACCOUNT
# ======================
@app.get("/account")
def account_home():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/account_home.html")

# ======================
# RECHARGE - STEP 1
# ======================
@app.route("/recharge/select-contact")
def select_contact():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("recharge/select_contact.html")

# ======================
# RECHARGE - STEP 1 : CONTACT / NUMÉRO
# ======================



    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        session["recharge_phone"] = phone
        return redirect(url_for("recharge_amount"))

    return render_template("recharge/select_contact.html")



    if request.method == "POST":
        phone = request.form.get("phone", "").strip()

        if not phone:
            return render_template(
                "recharge/select_contact.html",
                error="Veuillez entrer un numéro"
            )

        session["recharge_phone"] = phone
        return redirect(url_for("recharge_amount"))

    return render_template("recharge/select_contact.html")

        

    return render_template("recharge/select_contact.html")


@app.get("/account/profile")
def account_profile():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/profile.html")


@app.get("/account/payment-methods")
def account_payment_methods():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/payment_methods.html")


@app.get("/account/recurring")
def account_recurring_list():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/recurring_list.html")


@app.get("/account/notifications")
def account_notifications():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/notifications.html")


@app.get("/account/settings")
def account_settings():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/settings.html")


@app.get("/account/about")
def account_about():
    if not require_login():
        return redirect(url_for("login"))
    return render_template("account/about.html")


# ======================
# RECHARGE FLOW
# ======================
@app.route("/recharge/number", methods=["GET", "POST"])
def recharge_number():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        if not phone:
            flash("Numéro obligatoire.", "danger")
            return redirect(url_for("recharge_number"))

        session["recharge_phone"] = phone
        return redirect(url_for("recharge_amount"))

    return render_template("recharge/enter_number.html")


@app.route("/recharge/amount", methods=["GET", "POST"])
def recharge_amount():
    if not require_login():
        return redirect(url_for("login"))

    if "recharge_phone" not in session:
        return redirect(url_for("recharge_number"))

    if request.method == "POST":
        session["amount"] = request.form.get("amount")
        session["currency"] = request.form.get("currency")
        return redirect(url_for("order_summary"))

    return render_template("recharge/select_amount.html")


    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        currency = request.form.get("currency", "EUR").strip().upper()

        if not amount:
            flash("Montant obligatoire.", "danger")
            return redirect(url_for("recharge_amount"))

        if currency not in ("EUR", "USD"):
            currency = "EUR"

        recharge = create_recharge(
            user_id=session["user_id"],
            phone_number=session["recharge_phone"],
            amount=float(amount),
            currency=currency,
            operator="AUTO",
        )

        session["recharge_id"] = recharge["id"]
        return redirect(url_for("recharge_summary"))

    return render_template("recharge/select_amount.html")


@app.get("/recharge/summary")
def recharge_summary():
    if not require_login():
        return redirect(url_for("login"))

    phone = session.get("recharge_phone")
    amount = session.get("amount")
    currency = session.get("currency")

    # sécurité : si une étape manque
    if not phone or not amount or not currency:
        return redirect(url_for("recharge_number"))

    return render_template(
        "recharge/order_summary.html",
        phone=phone,
        amount=amount,
        currency=currency
    )


    recharge_id = session.get("recharge_id")
    if not recharge_id:
        return redirect(url_for("recharge_number"))

    recharge = get_recharge(recharge_id, session["user_id"])
    return render_template("recharge/order_summary.html", recharge=recharge)


@app.route("/recharge/payment", methods=["GET", "POST"])
def recharge_payment():
    if not require_login():
        return redirect(url_for("login"))

    phone = session.get("recharge_phone")
    amount = session.get("amount")
    currency = session.get("currency")

    # Sécurité : empêcher accès direct
    if not phone or not amount or not currency:
        return redirect(url_for("recharge_number"))

    if request.method == "POST":
        # ⚠️ Paiement simulé (fake)
        session["payment_status"] = "paid"
        return redirect(url_for("recharge_success"))

    return render_template(
        "recharge/payment.html",
        phone=phone,
        amount=amount,
        currency=currency
    )


    recharge_id = session.get("recharge_id")
    if not recharge_id:
        return redirect(url_for("recharge_number"))

    recharge = get_recharge(recharge_id, session["user_id"])

    if request.method == "POST":
        mark_paid(recharge_id, session["user_id"])
        return redirect(url_for("recharge_success"))

    return render_template("recharge/payment.html", recharge=recharge)



    # Vérifier que le paiement a bien été effectué
    if session.get("payment_status") != "paid":
        return redirect(url_for("dashboard"))

    phone = session.get("recharge_phone")
    amount = session.get("amount")
    currency = session.get("currency")

    # Nettoyage de la session (important)
    session.pop("recharge_phone", None)
    session.pop("amount", None)
    session.pop("currency", None)
    session.pop("payment_status", None)

    return render_template(
        "recharge/payment_success.html",
        phone=phone,
        amount=amount,
        currency=currency
    )

    recharge_id = session.get("recharge_id")
    if not recharge_id:
        return redirect(url_for("recharge_number"))

    recharge = get_recharge(recharge_id, session["user_id"])

    session.pop("recharge_phone", None)
    session.pop("recharge_id", None)

    return render_template("recharge/payment_success.html", recharge=recharge)


# ======================
# ERRORS
# ======================
@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


# ======================
# START APP
# ======================
if __name__ == "__main__":
    init_db()  # ✅ création DB au démarrage
    app.run(debug=True)