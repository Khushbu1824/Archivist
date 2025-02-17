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
    
@app.route('/books')
def books():
    books_list = [
        {
            "bookID": "35460",
            "title": "Star Wars: Clone Wars Adventures Volume 6",
            "authors": "W. Haden Blackman",
            "average_rating": "3.78",
            "isbn": "1593075677",
            "language_code": "eng",
            "num_pages": "88",
            "ratings_count": "176",
            "text_reviews_count": "10",
            "publication_date": "2006-08-23",
            "publisher": "Dark Horse Books",
            "genre": "Science Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "17828",
            "title": "The Master and Margarita",
            "authors": "Mikhail Bulgakov",
            "average_rating": "4.30",
            "isbn": "1411683056",
            "language_code": "eng",
            "num_pages": "332",
            "ratings_count": "493",
            "text_reviews_count": "47",
            "publication_date": "2006-04-01",
            "publisher": "Lulu Press",
            "genre": "Classic Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1001",
            "title": "To Kill a Mockingbird",
            "authors": "Harper Lee",
            "average_rating": "4.28",
            "isbn": "0061120081",
            "language_code": "eng",
            "num_pages": "324",
            "ratings_count": "4500",
            "text_reviews_count": "380",
            "publication_date": "1960-07-11",
            "publisher": "J.B. Lippincott & Co.",
            "genre": "Classic Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1002",
            "title": "1984",
            "authors": "George Orwell",
            "average_rating": "4.19",
            "isbn": "0451524934",
            "language_code": "eng",
            "num_pages": "328",
            "ratings_count": "5200",
            "text_reviews_count": "500",
            "publication_date": "1949-06-08",
            "publisher": "Secker & Warburg",
            "genre": "Dystopian Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1003",
            "title": "Pride and Prejudice",
            "authors": "Jane Austen",
            "average_rating": "4.27",
            "isbn": "9780141439518",
            "language_code": "eng",
            "num_pages": "279",
            "ratings_count": "3800",
            "text_reviews_count": "320",
            "publication_date": "1813-01-28",
            "publisher": "T. Egerton",
            "genre": "Romance",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1004",
            "title": "The Hobbit",
            "authors": "J.R.R. Tolkien",
            "average_rating": "4.28",
            "isbn": "9780547928227",
            "language_code": "eng",
            "num_pages": "310",
            "ratings_count": "5000",
            "text_reviews_count": "450",
            "publication_date": "1937-09-21",
            "publisher": "Allen & Unwin",
            "genre": "Fantasy",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1005",
            "title": "Harry Potter and the Sorcerer's Stone",
            "authors": "J.K. Rowling",
            "average_rating": "4.47",
            "isbn": "9780590353427",
            "language_code": "eng",
            "num_pages": "309",
            "ratings_count": "7000",
            "text_reviews_count": "600",
            "publication_date": "1997-06-26",
            "publisher": "Scholastic",
            "genre": "Fantasy",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1006",
            "title": "The Catcher in the Rye",
            "authors": "J.D. Salinger",
            "average_rating": "3.80",
            "isbn": "9780316769488",
            "language_code": "eng",
            "num_pages": "277",
            "ratings_count": "3000",
            "text_reviews_count": "290",
            "publication_date": "1951-07-16",
            "publisher": "Little, Brown and Company",
            "genre": "Classic Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1007",
            "title": "The Great Gatsby",
            "authors": "F. Scott Fitzgerald",
            "average_rating": "3.93",
            "isbn": "9780743273565",
            "language_code": "eng",
            "num_pages": "180",
            "ratings_count": "3600",
            "text_reviews_count": "310",
            "publication_date": "1925-04-10",
            "publisher": "Charles Scribner's Sons",
            "genre": "Classic Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        },
        {
            "bookID": "1008",
            "title": "Moby-Dick",
            "authors": "Herman Melville",
            "average_rating": "3.10",
            "isbn": "9781503280786",
            "language_code": "eng",
            "num_pages": "635",
            "ratings_count": "1500",
            "text_reviews_count": "120",
            "publication_date": "1851-11-14",
            "publisher": "Harper & Brothers",
            "genre": "Adventure Fiction",
            "book_image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSYB7PYeaa8Xtnn4YEJOjI6nxbyrd0QB0g4sg&s"
        }
    ]


    """
    books_list = Book.select().dicts()
    """

    return render_template("books.html", books=books_list)


@app.route('/transactions', methods=['POST'])
def transactions():
    issued_books = request.form.get("issuedBooks")

    if issued_books:
        # issued_books = json.loads(issued_books)  
        # book_ids = [book["bookId"] for book in issued_books]  

        # books_data = Book.select().where(Book.book_id.in_(book_ids))

        # book_list = [{"title": book.title, "isbn": book.isbn} for book in books_data]

        return render_template("transactions.html")

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

