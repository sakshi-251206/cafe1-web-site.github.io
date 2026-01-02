from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ================= MYSQL CONNECTION =================
try:
    db = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )
    cursor = db.cursor(dictionary=True)
    print("Database connected successfully!")
except mysql.connector.Error as e:
    print(f"Error connecting to database: {e}")


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

# ================= CONTACT =================
@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    sql = """
        INSERT INTO contact_messages (name, email, message)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (name, email, message))
    db.commit()

    return redirect("/")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        sql = """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (username, email, password))
        db.commit()

        return redirect("/login")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()

        if user:
            session["user"] = user["username"]
            return redirect("/")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use Railway's dynamic port or fallback to 5000
    app.run(host="0.0.0.0", port=port, debug=True)  # debug=True helps in logs
