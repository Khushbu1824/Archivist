from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, session
from datetime import datetime
from models import Book, Membership, Transaction, Admin, db
from weasyprint import HTML
from peewee import fn
from bcrypt import checkpw

import json
import requests
import traceback

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/2703')
def admin():
    
    try:
        if db.is_closed():
            db.connect()
        print("Database connected:", not db.is_closed(), flush=True)
        
        # Fetch total books
        total_books = Book.select(fn.SUM(Book.num_books_available)).scalar() or 0
        
        total_members = Membership.select().count()

        borrowed_books = Transaction.select().where(Transaction.status == "issued").count()

        current_date = datetime.today().date()  # Correct way to get today's date

        # Count transactions where return_date has passed
        overdue_books = Transaction.select().where(
            (Transaction.return_date < current_date) & (Transaction.status == "Issued")
        ).count()
        overdue_transactions = (
            Transaction.select()
            .where((Transaction.return_date < current_date) & (Transaction.status == "Issued"))
            .order_by(Transaction.return_date)
        )

        return render_template('admin.html', total_books=total_books, total_members=total_members,
                            borrowed_books=borrowed_books, overdue_books=overdue_books, overdue_transactions=overdue_transactions)

    except Exception as e:
        print("Error:", str(e), flush=True)
        return render_template('admin.html', error=str(e))
    
@bp.route('/login/2703', methods=['GET', 'POST'])
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
                return redirect(url_for('admin.admin'))  # Redirect to admin dashboard
            else:
                flash("Invalid username or password")
                return render_template('admin-login.html')  # Re-render login form
        else:
            flash("Invalid username or password")
            return render_template('admin-login.html')

    return render_template('admin-login.html')