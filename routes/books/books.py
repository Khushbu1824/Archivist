from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from datetime import datetime
from models import Book, Membership, Transaction, db
from weasyprint import HTML
import json
import requests
import traceback

bp = Blueprint('books', __name__, url_prefix='/books')

def get_book_data_for_template():
    books_list = Book.select()
    authors = Book.select(Book.authors).distinct().scalars()
    genres = Book.select(Book.genre).distinct().scalars()
    return books_list, authors, genres

def handle_book_form(book, template_name, redirect_url):
    if request.method == 'POST':
        try:
            if db.is_closed():
                db.connect()

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
            return redirect(url_for(redirect_url))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            print(f"Error: {e}")
            return render_template(template_name, book=book)

        finally:
            if not db.is_closed():
                db.close()

    return render_template(template_name, book=book)

@bp.route('/')
def books():
    books_list, authors, genres = get_book_data_for_template()
    return render_template("books.html", books=books_list, authors=authors, genres=genres)

@bp.route('/<int:membership_id>')
def bookslist(membership_id):
    books_list, authors, genres = get_book_data_for_template()
    return render_template("books.html", books=books_list, authors=authors, genres=genres, membership_id=membership_id)

@bp.route('/add-book', methods=['GET', 'POST'])
def add_book():
    book = Book()
    return handle_book_form(book, 'add-book.html', 'books.librarian_books')

@bp.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    try:
        book = Book.get(Book.book_id == book_id)
    except Book.DoesNotExist:
        flash("Book not found!", "danger")
        return redirect(url_for('books'))
    return handle_book_form(book, 'edit-book.html', 'books.librarian_books')

@bp.route('/librarian_books')
def librarian_books():
    books_ls = Book.select()
    return render_template('librarian-books.html', books=books_ls)

@bp.route('/delete-book/<int:book_id>')
def delete_book(book_id):
    book = Book.get_or_none(Book.book_id == book_id)
    if book:
        book.delete_instance()
    return redirect(url_for('books.librarian_books'))

@bp.route('/transactions', methods=['POST'])
def transactions():
    issued_books_json = request.form.get("issuedBooks")
    membership_id = request.form.get("membership_id")

    if issued_books_json:
        try:
            issued_books = json.loads(issued_books_json)
            book_ids = [book["bookId"] for book in issued_books]

            books_data = Book.select().where(Book.book_id.in_(book_ids))
            book_list = [{"title": book.title, "isbn": book.isbn} for book in books_data]
            return render_template("transactions.html", issued_books=book_list, membership_id=membership_id)
        except json.JSONDecodeError:
            return "Invalid JSON data", 400
    else:
        return "No books issued", 400

@bp.route("/issue-book/<int:membership_id>", methods=["GET", "POST"])
def issue_book_form(membership_id):
    membership = Membership.get_by_id(membership_id)
    if request.method == "POST":
        issued_books_json = request.form.get("issuedBooks")
        issued_books = []
        if issued_books_json:
            try:
                issued_books = json.loads(issued_books_json)
            except json.JSONDecodeError:
                return "Invalid JSON data", 400
        return render_template("transactions.html", membership=membership, issued_books=issued_books, membership_id=membership_id)

    return render_template("books.html", membership=membership, membership_id=membership_id)

@bp.route("/process-transaction", methods=["POST"])
def process_transaction():
    try:
        if db.is_closed():
            db.connect()

        user_id = int(request.form["membership_id"])
        issue_date = datetime.strptime(request.form["issue_date"], "%Y-%m-%d").date()
        return_date = datetime.strptime(request.form["return_date"], "%Y-%m-%d").date()
        status = request.form["status"]

        book_ids = request.form.getlist("book_ids")

        if not book_ids:
            return "No books selected", 400

        issued_books_list = []
        with db.atomic():
            for book_id in book_ids:
                book_id = int(book_id)
                book = Book.get_by_id(book_id)

                book_title = book.title
                isbn = book.isbn
                Transaction.create(
                    user_id=user_id,
                    book_id=book_id,
                    title=book_title,
                    isbn=isbn,
                    issue_date=issue_date,
                    return_date=return_date,
                    status=status
                )

                book.num_books_available -= 1  
                book.save()

                issued_books_list.append({
                    "book_id": book_id,
                    "title": book_title,
                    "authors": book.authors,
                    "isbn": isbn
                })

        return render_template("success-page.html", membership_id=user_id, issued_books=issued_books_list)

    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('books'))

    finally:
        if not db.is_closed():
            db.close()

@bp.route("/download/<int:membership_id>", methods=["POST"])
def download_pdf(membership_id):
        try:
            membership = Membership.get_by_id(membership_id)

            # Retrieve issued books from form input
            issued_books_json = request.form.get("issued_books")
            if not issued_books_json:
                return "No books provided", 400

            try:
                issued_books = json.loads(issued_books_json)
            except json.JSONDecodeError:
                return "Invalid JSON data", 400

            html = HTML(string=render_template("print/invoice.html", membership=membership, issued_books=issued_books))
            response = make_response(html.write_pdf())

            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = f'attachment; filename="issued_books_{membership_id}.pdf"'

            return response

        except Membership.DoesNotExist:
            return "Membership not found", 404
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
            
@bp.route("/return-books/<int:membership_id>")
def return_books(membership_id):
    try:
        if db.is_closed():
            db.connect()

        transactions = (
            Transaction.select(Transaction.transaction_id, Book.book_id, Book.title, Book.authors)
            .join(Book)
            .where((Transaction.user_id == membership_id) & (Transaction.status == "Issued"))
        )

        books = [
            {"transaction_id": t.transaction_id, "book_id": t.book.book_id, "title": t.book.title, "author": t.book.authors}
            for t in transactions
        ]

        return render_template("return-books.html", books=books, membership_id=membership_id)

    finally:
        if not db.is_closed():
            db.close()


@bp.route("/return-book", methods=["POST"])
def return_book():
    try:
        transaction_id = request.form.get("transaction_id")
        liked = request.form.get("liked") == "true"
        book_id = request.form.get("book_id")
        rating = int(request.form.get("rating", 0))

        if db.is_closed():
            db.connect()

        transaction = Transaction.get_or_none(Transaction.transaction_id == transaction_id)
        if not transaction:
            return jsonify({"success": False, "message": "Transaction not found."})

        return_date = transaction.return_date
        current_date = datetime.now().date()

        fine = 0
        if return_date < current_date:
            overdue_days = (current_date - return_date).days
            fine = 100 + (overdue_days * 10)

        with db.atomic():
            Transaction.update(status="Returned").where(Transaction.transaction_id == transaction_id).execute()
            Book.update(num_books_available=Book.num_books_available + 1).where(Book.book_id == book_id).execute()

            if liked:
                Book.update(likes=Book.likes + 1).where(Book.book_id == book_id).execute()

            if rating > 0:
                try:
                    book = Book.get(Book.book_id == book_id)
                    new_rating_count = book.ratings_count + 1
                    new_total_rating = (book.average_rating * book.ratings_count) + rating
                    new_average_rating = round(new_total_rating / new_rating_count, 2)
                    Book.update(ratings_count=new_rating_count, average_rating=new_average_rating).where(Book.book_id == book_id).execute()
                except Book.DoesNotExist:
                    print(f"Book not found for rating update: {book_id}")

        return jsonify({"success": True, "message": "Book returned successfully.", "fine": fine})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)})

    finally:
        if not db.is_closed():
            db.close()

@bp.route('/import-books', methods=['GET', 'POST'])
def import_books():
    if request.method == 'POST':
        try:
            if db.is_closed():
                db.connect()

            params = {
                'page': request.form.get('page', 1),
                'title': request.form.get('title'),
                'authors': request.form.get('authors'),
                'isbn': request.form.get('isbn'),
                'publisher': request.form.get('publisher')
            }
            num_books, imported_count = int(request.form.get('num_books', 20)), 0

            while imported_count < num_books:
                response = requests.get("https://frappe.io/api/method/frappe-library", params={k: v for k, v in params.items() if v})
                books = response.json().get('message', []) if response.status_code == 200 else []

                if not books:
                    break

                for book in books:
                    if imported_count >= num_books:
                        break
                    try:
                        with db.atomic():
                            Book.create(
                                title=book.get('title'),
                                authors=book.get('authors'),
                                average_rating=float(book.get('average_rating', 0)),
                                isbn=book.get('isbn'),
                                isbn13=book.get('isbn13'),
                                language_code=book.get('language_code'),
                                num_pages=int(book.get('num_pages', 0)),
                                ratings_count=int(book.get('ratings_count', 0)),
                                text_reviews_count=int(book.get('text_reviews_count', 0)),
                                publication_date=datetime.strptime(book.get('publication_date', ''), '%m/%d/%Y').date() if book.get('publication_date') else None,
                                publisher=book.get('publisher'),
                                genre=book.get('genre'),
                                book_image=book.get('book_image'),
                                likes=int(book.get('likes', 0)),
                                num_books_available=int(book.get('num_books_available', 1))
                            )
                        imported_count += 1
                    except Exception as e:
                        print(f"Error importing book {book.get('title')}: {e}")

                params['page'] = int(params['page']) + 1

            flash(f"{imported_count} books imported successfully!")
            return redirect(url_for('librarian_books'))

        except Exception as e:
            flash(f"An error occurred: {e}")

        finally:
            if not db.is_closed():
                db.close()

    return render_template('import_books.html')
