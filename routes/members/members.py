from flask import Flask, Blueprint, render_template, request, redirect, flash, session, url_for, jsonify, Response
from bcrypt import hashpw, gensalt, checkpw
from models import initialize_db, Book, Membership, Admin, Transaction, db
from datetime import datetime
import json 
import requests
import csv
import io

bp = Blueprint('members', __name__, url_prefix='/members')

@bp.route("/new-membership")
def create_membership_form():
    return render_template("create-membership.html")

@bp.route("/register", methods=["POST"])
def register():
    try:
        if db.is_closed():
            db.connect()

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
        
@bp.route('/')
def members():
    members_ls = Membership.select()
    return render_template('members.html', members=members_ls)

@bp.route('/delete/<int:membership_id>')
def delete_member(membership_id):
    member = Membership.get_or_none(Membership.membership_id == membership_id)  # Assuming your Member model has a member_id

    if member is None:
        return "Member not found", 404

    member.delete_instance()
    return redirect(url_for('members.members'))

@bp.route('/edit/<int:member_id>', methods=['GET', 'POST'])
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
            return render_template('edit-member.html', member=member)  # Pass the member object

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
        return redirect(url_for('members.members'))  # Redirect to the correct route

    return render_template('edit-member.html', member=member)

@bp.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('books.bookslist', membership_id=membership.membership_id))
            else:
                error_message = 'Incorrect password'
        else:
            error_message = 'User not found'

        return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@bp.route('/membership-renewal/<int:id>', methods=['GET', 'POST'])
def membership_renewal(id):
    try:
        membership = Membership.get_by_id(id)
    except Membership.DoesNotExist:
        flash("Membership record not found.")
        return redirect(url_for('books.books'))

    if request.method == 'GET':
        return render_template('membership-renewal.html', membership=membership)

    elif request.method == 'POST':
        try:
            new_expiry_date_str = request.form.get('new_expiry_date')
            new_expiry_date = datetime.strptime(new_expiry_date_str, '%Y-%m-%d').date() # Corrected line

            membership.membership_expiry_date = new_expiry_date
            membership.save()
            flash("Membership updated successfully!")
            return redirect(url_for('books.books'))

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return render_template('membership-renewal.html', membership=membership)
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return render_template('membership-renewal.html', membership=membership)

@bp.route('/download-csv')
def download_csv():
    members_ls = Membership.select()

    # Create a string buffer to hold the CSV data
    output = io.StringIO()
    writer = csv.writer(output)

    # Write the header
    writer.writerow(["S No.", "Name", "Membership Start Date", "Membership Expiry Date", "Status"])

    # Write member data
    for index, member in enumerate(members_ls, start=1):
        writer.writerow([index, member.name, member.membership_start_date, member.membership_expiry_date, member.status])

    # Get CSV data from buffer
    output.seek(0)

    # Create a Flask Response with CSV data
    response = Response(output.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=members_list.csv"
    
    return response