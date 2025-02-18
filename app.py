from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from bcrypt import hashpw, gensalt, checkpw
from models import initialize_db, Book, Membership, Admin, Transaction, db
from datetime import datetime
import json 
import requests
from peewee import fn


def create_app():

    app = Flask(__name__)
    app.secret_key = "12345"

    initialize_db()

    from routes.books.books import bp as books  # Correct import
    app.register_blueprint(books)

    from routes.members.members import bp as members  # Correct import
    app.register_blueprint(members)

    from routes.admin.admin import bp as admin  # Correct import
    app.register_blueprint(admin)

    @app.route('/')
    def home():
        return render_template("home.html")
    
    @app.route('/issued_books/<int:membership_id>')
    def issued_books(membership_id):
        return render_template("success-page.html", membership_id=membership_id)

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
