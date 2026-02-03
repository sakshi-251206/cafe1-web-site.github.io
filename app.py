from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

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
        flash("Database connection not available.", "danger")
        return redirect("/")

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        flash("All fields are required.", "warning")
        return redirect("/")

    try:
        sql = "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, message))
        db.commit()
        flash("Message sent successfully!", "success")
        return redirect("/")
    except mysql.connector.Error as e:
        flash(f"Database error: {e}", "danger")
        return redirect("/")
    except Exception as e:
        flash(f"Unexpected error: {e}", "danger")
        return redirect("/")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if not cursor:
        flash("Database connection not available.", "danger")
        return redirect("/")

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("All fields are required.", "warning")
            return redirect("/register")

        try:
            # Hash the password
            hashed_password = generate_password_hash(password)
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, email, hashed_password))
            db.commit()
            flash("Registration successful! Please login.", "success")
            return redirect("/login")
        except mysql.connector.IntegrityError:
            flash("Email already exists.", "danger")
            return redirect("/register")
        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect("/register")
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
            return redirect("/register")

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if not cursor:
        flash("Database connection not available.", "danger")
        return redirect("/")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and Password are required.", "warning")
            return redirect("/login")

        try:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):
                session["user"] = user["username"]
                flash(f"Welcome, {user['username']}!", "success")
                return redirect("/")
            else:
                flash("Invalid Email or Password.", "danger")
                return redirect("/login")
        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")
            return redirect("/login")
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
            return redirect("/login")

    return render_template("login.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
