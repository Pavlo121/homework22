from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('greeting/', views.greeting_view, name='greeting'),
    path('logout/', views.logout_view, name='logout'),
    path('books/statistics/', views.books_statistics, name='books_statistics'),
    path('books/raw-sql/', views.raw_sql_statistics, name='raw_sql_statistics'),
    path('books/', views.book_list, name='book_list'),
]
