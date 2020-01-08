from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('author-detail/<int:pk>', views.AuthorDetail.as_view(), name='author-detail'),
]