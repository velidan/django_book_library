from django.urls import path, include, re_path
from . import views

# rest_framework 
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('author-detail/<int:pk>', views.AuthorDetail.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBookByUserListView.as_view(), name='my-borrowed'),
    path('library-books', views.LibraryBooksListView.as_view(), name='library-books'),
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [  
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

urlpatterns += [  
    path('book/create/', views.BookCreate.as_view(), name='book_create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]

# rest 
urlpatterns += [  
    path('books_rest/', views.BooksRest.as_view(), name='books_rest'),
    path('book_rest/<int:pk>/', views.BookRest.as_view(), name='book_rest'),
    path('authors_rest/', views.AuthorsRest.as_view(), name='authors_rest'),
    path('authors_rest/<int:pk>/', views.AuthorRest.as_view(), name='author_rest'),
    path('rest_root/', views.api_root, name='rest_root'),
    re_path(r'^api-auth/', include('rest_framework.urls')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
