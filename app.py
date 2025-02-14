from flask import Flask, render_template, request, redirect, flash
from bcrypt import hashpw, gensalt
from models import initialize_db, Membership, db # Import the function to initialize DB
from datetime import datetime

app = Flask(__name__)
app.secret_key = "12345"

# Initialize the database when the app starts
initialize_db()

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route("/new-membership")
def create_membership_form():
    return render_template("create-membership.html")

@app.route("/register", methods=["POST"])
def register():
    try:
        if db.is_closed():
            db.connect()
        # Retrieve form data
        name = request.form["name"]
        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d").date()
        email = request.form["email"]
        contact_no = request.form["contact_no"]
        password = request.form["password"]  # Store securely in production!
        address = request.form["address"]
        membership_type = request.form["membership_type"]
        membership_start_date = datetime.strptime(request.form["membership_start_date"], "%Y-%m-%d").date()
        membership_expiry_date = datetime.strptime(request.form["membership_expiry_date"], "%Y-%m-%d").date()

        hashed_password = hashpw(password.encode(), gensalt()).decode()

        print(f"Attempting to insert: {name}, {email}, {contact_no}")
        # Insert into database
        with db.atomic():  # Ensures transaction safety
            Membership.create(
                name=name,
                dob=dob,
                email=email,
                contact_no=contact_no,
                password = hashed_password,
                address=address,
                membership_type=membership_type,
                membership_start_date=membership_start_date,
                membership_expiry_date=membership_expiry_date,
                status="Active"
            )
        print("Data Inserted Successfully!")  # Debugging

        flash("Registration successful!", "success")
        return redirect("/new-membership")

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        print(f"Database Error: {e}")  # Debugging
        return redirect("/new-membership")
    
    finally:
        if not db.is_closed():
            db.close()  # Close connection after operation

if __name__ == '__main__':
    app.run(debug=True)