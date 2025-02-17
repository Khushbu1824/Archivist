from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify, make_response
from bcrypt import hashpw, gensalt, checkpw
from models import initialize_db, Book, Membership, Admin, db
from datetime import datetime
from weasyprint import HTML
import json 

app = Flask(__name__)
app.secret_key = "12345"

# Initialize the database when the app starts
initialize_db()

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        membership = Membership.get_or_none(Membership.email == email)

        if membership:
            stored_hash = membership.password

            entered_password_encoded = password.encode('utf-8')

            # Decode the stored hash from memoryview to bytes if needed
            if isinstance(stored_hash, memoryview):
                stored_hash = bytes(stored_hash)  # Convert memoryview to bytes

            if checkpw(entered_password_encoded, stored_hash):
                session['user_id'] = membership.membership_id  # Store user_id in session
                return redirect(url_for('bookslist', membership_id=membership.membership_id))
            else:
                error_message = 'Incorrect password'
        else:
            error_message = 'User not found'

        return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.get_or_none(Admin.username == username)

        if admin:
            stored_hash = admin.password

            entered_password_encoded = password.encode('utf-8')

            if isinstance(stored_hash, memoryview):
                stored_hash = bytes(stored_hash)


            if checkpw(entered_password_encoded, stored_hash):
                session['admin_logged_in'] = True  # Set session variable
                session['user_type'] = 'admin' #Set user type to admin in session
                return redirect(url_for('librarian_books'))  # Redirect to admin dashboard
            else:
                flash("Invalid username or password")
                return render_template('admin_login.html')  # Re-render login form
        else:
            flash("Invalid username or password")
            return render_template('admin_login.html')

    return render_template('admin-login.html')

@app.route('/books')
def books():
    # Retrieve all books from the database
    books_list = Book.select()
    authors = Book.select(Book.authors).distinct().scalars()
    genres = Book.select(Book.genre).distinct().scalars()
    return render_template("books.html", books=books_list, authors=authors, genres=genres)

@app.route('/books/<int:membership_id>')
def bookslist(membership_id):
    # Retrieve all books from the database
    books_list = Book.select()
    authors = Book.select(Book.authors).distinct().scalars()
    genres = Book.select(Book.genre).distinct().scalars()
    return render_template("books.html", books=books_list, authors=authors, genres=genres)
    
@app.route('/transactions', methods=['POST'])
def transactions():
    issued_books_json = request.form.get("issuedBooks")

    if issued_books_json:
        try:
            issued_books = json.loads(issued_books_json)  # Crucial: Parse the JSON string
            book_ids = [book["bookId"] for book in issued_books]

            books_data = Book.select().where(Book.book_id.in_(book_ids)) #Query database

            book_list = [{"title": book.title, "isbn": book.isbn} for book in books_data] #Create list of book details
            
            return render_template("transactions.html", issued_books=book_list)  # Pass data to template
        except json.JSONDecodeError:
            return "Invalid JSON data", 400  # Handle JSON parsing errors
    else:
        return "No books issued", 400 #Handle no books issued error

    return jsonify({"success": False, "message": "No books issued!"})

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

        hashed_password_bytes = hashpw(password.encode('utf-8'), gensalt()) 

        print(f"Attempting to insert: {name}, {email}, {contact_no}")
        # Insert into database
        with db.atomic():  # Ensures transaction safety
            Membership.create(
                name=name,
                dob=dob,
                email=email,
                contact_no=contact_no,
                password=hashed_password_bytes,
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

