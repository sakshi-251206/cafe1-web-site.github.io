from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "default_secret_key"

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
    print("✅ Database connected successfully!")
except mysql.connector.Error as e:
    print(f"❌ Error connecting to database: {e}")
    cursor = None
    db = None

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

# ================= CONTACT =================
@app.route("/contact", methods=["POST"])
def contact():
    if not cursor:
        return "Database connection not available."

    try:
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            return "All fields are required."

        sql = "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, message))
        db.commit()
        return redirect("/")
    except mysql.connector.Error as e:
        return f"Database error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if not cursor:
        return "Database connection not available."

    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            if not username or not email or not password:
                return "All fields are required."

            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, email, password))
            db.commit()
            return redirect("/login")
        except mysql.connector.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if not cursor:
        return "Database connection not available."

    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                return "Email and Password are required."

            sql = "SELECT * FROM users WHERE email=%s AND password=%s"
            cursor.execute(sql, (email, password))
            user = cursor.fetchone()

            if user:
                session["user"] = user["username"]
                return redirect("/")
            else:
                return "Invalid Email or Password"
        except mysql.connector.Error as e:
            return f"Database error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # dynamic port for deployment
    app.run(host="0.0.0.0", port=port, debug=True)
