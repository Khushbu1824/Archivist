import os
from dotenv import load_dotenv
from peewee import Model, PostgresqlDatabase, CharField, IntegerField, FloatField, DateField

load_dotenv()

DATABASE = {
    'name': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT'))
}

db = PostgresqlDatabase(
    DATABASE['name'],
    user=DATABASE['user'],
    password=DATABASE['password'],
    host=DATABASE['host'],
    port=DATABASE['port']
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
