from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "secret-key"

# ================= LANGUES =================

TEXT = {
    "en": {
        "home": "Home",
        "recharge": "Recharge",
        "history": "History",
        "account": "Account",
        "welcome": "Welcome to Tikzok",
        "subtitle": "Fast and secure mobile recharge",
        "start": "Start recharge",
        "language": "Language",
    },
    "tr": {
        "home": "Ana Sayfa",
        "recharge": "Yükleme",
        "history": "Geçmiş",
       "account": "Hesap",
        "welcome": "Tikzok'a Hoş Geldiniz",
        "subtitle": "Hızlı ve güvenli mobil yükleme",
        "start": "Yüklemeye başla",
        "language": "Dil",
    },
    "fa": {
        "home": "خانه",
        "recharge": "شارژ",
        "history": "تاریخچه",
        "account": "حساب",
        "welcome": "به Tikzok خوش آمدید",
        "subtitle": "شارژ موبایل سریع و امن",
        "start": "شروع شارژ",
        "language": "زبان",
    },
    "uz": {
        "home": "Bosh sahifa",
        "recharge": "To‘ldirish",
        "history": "Tarix",
        "account": "Hisob",
        "welcome": "Tikzokga xush kelibsiz",
        "subtitle": "Tez va xavfsiz mobil to‘ldirish",
        "start": "To‘ldirishni boshlash",
        "language": "Til",
    }
}

LANGS = [
    ("en", "English"),
    ("tr", "Türkçe"),
    ("fa", "فارسی"),
    ("uz", "Oʻzbek"),
]

def get_lang():
    return session.get("lang", "en")

def t(key):
    return TEXT[get_lang()].get(key, key)

@app.context_processor
def inject():
    return dict(t=t, langs=LANGS, current_lang=get_lang())

@app.route("/set-lang/<lang>")
def set_lang(lang):
    if lang in TEXT:
        session["lang"] = lang
    return redirect(request.referrer or url_for("accueil"))

# ================= PAGES =================

@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/recharge")
def recharge():
    return render_template("recharge.html")

@app.route("/historique")
def historique():
    return render_template("historique.html")

@app.route("/compte")
def compte():
    return render_template("compte.html")

# ================= RUN =================

@app.route("/compte")
def login():
    return render_template("login.html")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
