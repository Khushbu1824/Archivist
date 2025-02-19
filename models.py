import os
from dotenv import load_dotenv
from peewee import Model, AutoField, PostgresqlDatabase, CharField, IntegerField, FloatField, DateField, BlobField, ForeignKeyField

# Load environment variables from .env file
load_dotenv()

# Ensure all required database credentials are loaded
DATABASE = {
    'name': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# DATABASE_URL = os.getenv("SUPABASE_DB_URL")

# if not DATABASE_URL:
#     raise ValueError("SUPABASE_DB_URL is not set in environment variables!")

# db = PostgresqlDatabase(DATABASE_URL, autorollback=True)

# Connect to the PostgreSQL database
db = PostgresqlDatabase(
    DATABASE['name'],
    user=DATABASE['user'],
    password=DATABASE['password'],
    host=DATABASE['host'],
    port=int(DATABASE['port'])
)

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
    address = CharField(null=True)  # Optional field
    membership_type = CharField()  # E.g., Student, Faculty, Guest
    membership_start_date = DateField()
    membership_expiry_date = DateField()
    status = CharField(default="Active")  # Active, Inactive, Expired


class Transaction(BaseModel):
    transaction_id = AutoField()
    user = ForeignKeyField(Membership, backref="transactions", on_delete="CASCADE")
    book = ForeignKeyField(Book, backref="transactions", on_delete="CASCADE")
    isbn = CharField()
    title = CharField()
    issue_date = DateField()
    return_date = DateField(null=True)  # Nullable, as book may not be returned yet
    status = CharField(default="Issued")  # "Issued" or "Returned"

def initialize_db():
    db.connect()
    db.create_tables([Book, Membership, Admin, Transaction], safe=True)  # safe=True prevents errors if tables already exist
    db.close()
