from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from bcrypt import hashpw, gensalt, checkpw
from models import initialize_db, Book, Membership, Admin, Transaction, db
from datetime import datetime
import json 
import requests

def create_app():

    app = Flask(__name__)
    app.secret_key = "12345"

    initialize_db()

    from routes.books.books import bp as books  # Correct import
    app.register_blueprint(books)

    @app.route('/')
    def home():
        return render_template("home.html")

    @app.route('/admin/2703')
    def admin():
        
        try:
            if db.is_closed():
                db.connect()
            print("Database connected:", not db.is_closed(), flush=True)
            
            # Fetch total books
            total_books = Book.select(fn.SUM(Book.num_books_available)).scalar() or 0
            
            total_members = Membership.select().count()

            borrowed_books = Transaction.select().count()

            current_date = datetime.today().date()  # Correct way to get today's date

            # Count transactions where return_date has passed
            overdue_books = Transaction.select().where(Transaction.return_date < current_date).count()
            overdue_transactions = (
                Transaction.select()  # Select directly from Transaction
                .where(Transaction.return_date < current_date)
                .order_by(Transaction.return_date)
            )

            return render_template('admin.html', total_books=total_books, total_members=total_members,
                                borrowed_books=borrowed_books, overdue_books=overdue_books, overdue_transactions=overdue_transactions)

        except Exception as e:
            print("Error:", str(e), flush=True)
            return render_template('admin.html', error=str(e))



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

    @app.route('/admin/login/2703', methods=['GET', 'POST'])
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
                    return redirect(url_for('admin'))  # Redirect to admin dashboard
                else:
                    flash("Invalid username or password")
                    return render_template('admin-login.html')  # Re-render login form
            else:
                flash("Invalid username or password")
                return render_template('admin-login.html')

        return render_template('admin-login.html')

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
                new_member = Membership.create(
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

            return redirect(f"/books/{new_member.membership_id}")

        except Exception as e:
            print(f"Database Error: {e}")  # Debugging
            return redirect("/new-membership")
        
        finally:
            if not db.is_closed():
                db.close()  # Close connection after operation

    @app.route('/members')
    def members():
        members_ls = Membership.select()
        return render_template('members.html', members=members_ls)

    @app.route('/delete-member/<int:membership_id>')
    def delete_member(membership_id):
        member = Membership.get_or_none(Membership.membership_id == membership_id)  # Assuming your Member model has a member_id

        if member is None:
            return "Member not found", 404

        member.delete_instance()
        return redirect(url_for('members')) 

    @app.route('/edit-member/<int:member_id>', methods=['GET', 'POST'])
    def edit_member(member_id):
        try:
            member = Membership.get(Membership.membership_id == member_id)  # Correct way to get the member
        except Membership.DoesNotExist:  # Correct exception to catch
            flash("Member not found!", "danger")
            return redirect(url_for('members'))  # Redirect to the correct route

        if request.method == 'POST':
            member.name = request.form['name']  # Access attributes through the member object
            try:
                member.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date of birth format!", "danger")
                return render_template('edit-m3ember.html', member=member)  # Pass the member object

            member.email = request.form['email']
            member.contact_no = request.form['contact_no']
            member.address = request.form['address']
            member.status = request.form['status']

            if 'password' in request.form and request.form['password']:
                new_password = request.form['password']
                hashed_password_bytes = hashpw(new_password.encode('utf-8'), gensalt())
                member.password = hashed_password_bytes

            member.save()
            flash("Member updated successfully!", "success")
            return redirect(url_for('members'))  # Redirect to the correct route

        return render_template('edit-member.html', member=member) 

    @app.route('/membership-renewal/<int:id>', methods=['GET', 'POST'])
    def membership_renewal(id):
        try:
            membership = Membership.get_by_id(id)
        except Membership.DoesNotExist:
            flash("Membership record not found.")
            return redirect(url_for('books'))

        if request.method == 'GET':
            return render_template('membership-renewal.html', membership=membership)

        elif request.method == 'POST':
            try:
                new_expiry_date_str = request.form.get('new_expiry_date')
                new_expiry_date = datetime.strptime(new_expiry_date_str, '%Y-%m-%d').date() # Corrected line

                membership.membership_expiry_date = new_expiry_date
                membership.save()
                flash("Membership updated successfully!")
                return redirect(url_for('books'))

            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.")
                return render_template('membership-renewal.html', membership=membership)
            except Exception as e:
                flash(f"An error occurred: {str(e)}")
                return render_template('membership-renewal.html', membership=membership)

    @app.route('/issued_books/<int:membership_id>')
    def issued_books(membership_id):
        return render_template("success-page.html", membership_id=membership_id)

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
