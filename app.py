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

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            if db.is_closed():
                db.connect()

            title = request.form['title']
            authors = request.form['authors']
            average_rating = request.form.get('average_rating')
            isbn = request.form['isbn']
            isbn13 = request.form['isbn13']
            language_code = request.form['language_code']
            num_pages = request.form['num_pages']
            ratings_count = request.form.get('ratings_count')
            text_reviews_count = request.form.get('text_reviews_count')
            publication_date_str = request.form['publication_date']

            try:
                publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid publication date format!", "danger")
                return render_template('add-book.html')

            publisher = request.form['publisher']
            genre = request.form['genre']
            book_image = request.form['book_image']
            likes = request.form.get('likes')

            with db.atomic():
                Book.create(
                    title=title,
                    authors=authors,
                    average_rating=float(average_rating) if average_rating else 0.0,
                    isbn=isbn,
                    isbn13=isbn13,
                    language_code=language_code,
                    num_pages=int(num_pages) if num_pages else 0,  # Replace None with 0
                    ratings_count=int(ratings_count) if ratings_count else 0,  # Replace None with 0
                    text_reviews_count=int(text_reviews_count) if text_reviews_count else 0,  # Replace None with 0
                    publication_date=publication_date,
                    publisher=publisher,
                    genre=genre,
                    likes=int(likes) if likes else 0,
                    book_image=book_image
                )

            flash("Book added successfully!", "success")
            return redirect(url_for('books'))

        except Exception as e:
            flash(f"Error adding book: {str(e)}", "danger")
            print(f"Error: {e}")
            return render_template('add-book.html')

        finally:
            if not db.is_closed():
                db.close()

    return render_template('add-book.html')

@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    try:
        book = Book.get(Book.book_id == book_id)  # Fetch the book FIRST
    except Book.DoesNotExist:
        flash("Book not found!", "danger")
        return redirect(url_for('books'))  # Redirect to books list, not home

    if request.method == 'POST':
        book.title = request.form['title']
        book.authors = request.form['authors']
        book.average_rating = request.form['average_rating']
        book.isbn = request.form['isbn']
        book.isbn13 = request.form['isbn13']
        book.language_code = request.form['language_code']
        book.num_pages = request.form['num_pages']
        book.ratings_count = request.form['ratings_count']
        book.text_reviews_count = request.form['text_reviews_count']
        try:  # Handle potential date parsing errors
            book.publication_date = datetime.strptime(request.form['publication_date'], '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid publication date format!", "danger")
            return render_template('edit-book.html', book=book) #re-render the form with error

        book.publisher = request.form['publisher']
        book.genre = request.form['genre']
        book.likes = request.form['likes']
        book.book_image = request.form['book_image']

        book.save()
        flash("Book updated successfully!", "success")
        return redirect(url_for('books'))  # Redirect back to the book list

    return render_template('edit-book.html', book=book)

@app.route('/librarian_books')
def librarian_books():
    books_ls = Book.select()
    return render_template('librarian-books.html', books=books_ls)

@app.route('/delete-book/<int:book_id>')
def delete_book(book_id):
    book = Book.get_or_none(Book.book_id == book_id)

    if book is None:
        return "Book not found", 404

    book.delete_instance()  # Delete the book
    return redirect(url_for('librarian_books'))

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

@app.route('/members')
def members():
    members_ls = Membership.select()
    return render_template('members.html', members=members_ls)
    
if __name__ == '__main__':
    app.run(debug=True)

