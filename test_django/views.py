from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db.models import Avg, Count
from django.db import connection
from .models import Book, Author
from .forms import UserForm



# Форма входу
def login_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            age = form.cleaned_data['age']
            response = redirect('greeting')
            response.set_cookie('name', name, max_age=3600)
            request.session['age'] = age
            return response
    else:
        form = UserForm()
    return render(request, 'login.html', {'form': form})


# Привітання користувача
def greeting_view(request):
    name = request.COOKIES.get('name')
    age = request.session.get('age')
    if name and age:
        return render(request, 'greeting.html', {'name': name, 'age': age})
    return redirect('login')


# Вихід (видалення даних з cookies і сесії)
def logout_view(request):
    response = redirect('login')
    response.delete_cookie('name')
    if 'age' in request.session:
        del request.session['age']
    return response


# Список книг з кешуванням
def book_list(request):
    # Перевірка наявності даних у кеші
    books = cache.get('book_list')
    if not books:
        # Якщо кешу немає, завантажуємо з бази та кешуємо
        books = list(Book.objects.select_related('author').prefetch_related('reviews'))
        cache.set('book_list', books, 300)  # кешуємо на 5 хвилин
    return render(request, 'book_list.html', {'books': books})


# Оновлення книги і скидання кешу
def update_book(request, book_id):
    book = Book.objects.get(pk=book_id)
    book.title = 'Updated Title'  # Оновлюємо назву книги
    book.save()

    # Оновлюємо кеш, оскільки дані змінилися
    cache.delete('book_list')
    return redirect('book_list')


# Статистика книг
def books_statistics(request):
    # Використовуємо annotate для обчислення середнього рейтингу та кількості книг
    authors = Author.objects.annotate(
        avg_rating=Avg('books__reviews__rating'),
        book_count=Count('books')
    )

    books = Book.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count', '-avg_rating')  # Сортуємо по кількості відгуків і рейтингу

    context = {'authors': authors, 'books': books}
    return render(request, 'books_statistics.html', context)


# SQL-запити з сирим SQL

def raw_sql_statistics(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.id, a.name, COUNT(b.id) AS book_count
            FROM test_django_author a
            JOIN test_django_book b ON a.id = b.author_id
            JOIN test_django_review r ON b.id = r.book_id
            GROUP BY a.id 
            HAVING COUNT(r.id) > %s
        """, [10])
        authors = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM test_django_book")
        book_count = cursor.fetchone()[0]

    context = {'authors': authors, 'book_count': book_count}
    return render(request, 'raw_sql_statistics.html', context)