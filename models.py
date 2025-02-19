import os
from dotenv import load_dotenv
from peewee import (
    Model, AutoField, PostgresqlDatabase, CharField, IntegerField, 
    FloatField, DateField, BlobField, ForeignKeyField
)

# Load environment variables
load_dotenv()

# Use Supabase PostgreSQL connection
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL is not set in environment variables!")

db = PostgresqlDatabase(DATABASE_URL, autorollback=True)

class BaseModel(Model):
    class Meta:
        database = db

class Admin(BaseModel):
    admin_id = AutoField()
    username = CharField(unique=True)
    password = BlobField()  
    email = CharField(unique=True)
    image_url = CharField(null=True)  
    contact_no = CharField()

class Book(BaseModel):
    book_id = AutoField() 
    title = CharField()
    authors = CharField()
    average_rating = FloatField()
    isbn = CharField(unique=True)
    isbn13 = CharField(unique=True)
    language_code = CharField()
    num_pages = IntegerField()
    ratings_count = IntegerField()
    text_reviews_count = IntegerField()
    publication_date = DateField()
    publisher = CharField()
    genre = CharField()
    likes = IntegerField(default=0)
    book_image = CharField(null=True)
    num_books_available = IntegerField(default=0)

class Membership(BaseModel):
    membership_id = AutoField()
    name = CharField()
    dob = DateField()
    email = CharField(unique=True)
    contact_no = CharField()
    password = BlobField()
    address = CharField(null=True)
    membership_type = CharField()
    membership_start_date = DateField()
    membership_expiry_date = DateField()
    status = CharField(default="Active")

class Transaction(BaseModel):
    transaction_id = AutoField()
    user = ForeignKeyField(Membership, backref="transactions", on_delete="CASCADE")
    book = ForeignKeyField(Book, backref="transactions", on_delete="CASCADE")
    isbn = CharField()
    title = CharField()
    issue_date = DateField()
    return_date = DateField(null=True)
    status = CharField(default="Issued")

def initialize_db():
    db.connect()
    db.create_tables([Book, Membership, Admin, Transaction], safe=True)
    db.close()
