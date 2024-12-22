from .models import Author, Book, Review
import random
from faker import Faker

def generate_test_data():
    fake = Faker()
    authors = [Author(name=fake.name()) for _ in range(10)]
    Author.objects.bulk_create(authors)
    books = [Book(title=fake.catch_phrase(), author=random.choice(authors)) for _ in range(50)]
    Book.objects.bulk_create(books)
    reviews = [Review(content=fake.text(max_nb_chars=200), book=random.choice(books)) for _ in range(200)]
    Review.objects.bulk_create(reviews)

