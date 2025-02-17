import os
from dotenv import load_dotenv
from peewee import Model, PostgresqlDatabase, CharField, IntegerField, FloatField, DateField, AutoField

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

# Check if all required environment variables are set
missing_vars = [key for key, value in DATABASE.items() if value is None]
if missing_vars:
    raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

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

class Book(BaseModel):
    book_id = IntegerField(primary_key=True)
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


class Membership(BaseModel):
    membership_id = AutoField()
    name = CharField()
    dob = DateField()
    email = CharField(unique=True)
    contact_no = CharField()
    password = CharField()
    address = CharField(null=True)  # Optional field
    membership_type = CharField()  # E.g., Student, Faculty, Guest
    membership_start_date = DateField()
    membership_expiry_date = DateField()
    status = CharField(default="Active")  # Active, Inactive, Expired

def initialize_db():
    db.connect()
    db.create_tables([Book, Membership], safe=True)  # safe=True prevents errors if tables already exist
    db.close()
