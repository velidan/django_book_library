from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic, View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

import datetime
from catalog.forms import RenewBookForm
import catalog

# generic CRUD
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalog.models import Author, Book

# django rest framework
from catalog.serializers import BookSerializer, AuthorSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication, permissions, mixins, generics
from django.http import HttpResponse, JsonResponse, Http404
from catalog.permissions import CanMarkReturned
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    context_object_name = 'my_book_list' # own name for the list as a template variable
    queryset = Book.objects.all()

class BookDetailView(generic.DetailView):
    model = Book

class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    
     # By default, these views will redirect on success to a page displaying the newly created/edited model item
    model = Book
    fields = '__all__'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'

    model = Book
    fields = '__all__'

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'

    model = Book
    success_url = reverse_lazy('books')

class AuthorsView(generic.ListView):
    model = Author
    context_object_name = 'authors_list'
    queryset = Author.objects.all()
    template_name = 'catalog/authors.html'

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'

    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'

    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'

    model = Author
    success_url = reverse_lazy('authors')

class AuthorDetail(generic.DetailView):
    model = Author

class LoanedBookByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user) \
            .filter(status__exact='o') \
            .order_by('due_back')


class LibraryBooksListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view Library books of the users that took them"""
    permission_required = 'catalog.can_mark_returned'
    # or multiple
    # permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')

    model = BookInstance
    template_name = 'catalog/bookinstance_list_library.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects \
            .filter(status__exact='o') \
            .order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewinga specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as 
            # required (here we just write it to the model due_back field)

            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('library-books'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_data': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


# Django Rest Framework

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'books_rest': reverse('books_rest', request=request, format=format),
        'authors_rest': reverse('authors_rest', request=request, format=format)
    })

# --- Simplified mixin based solution


class BooksRest(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [ CanMarkReturned ]

    def perform_create(self, serializer):
        print(f'self.request.user => {dir(self.request.user)}')


class BookRest(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    permission_classes = [ CanMarkReturned ]


class AuthorsRest(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    

class AuthorRest(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

# --- mixin based solution
# class BooksRest(mixins.ListModelMixin,
#                 mixins.CreateModelMixin,
#                 generics.GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)


# class BookRest(mixins.RetrieveModelMixin,
#                 mixins.UpdateModelMixin,
#                 mixins.DestroyModelMixin,
#                 generics.GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def put(self, request, *args, **kwargs):
#         return self.update(request, *args, **kwargs)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)

#--- working class based APIView Books list + create

# class BooksRest(APIView):

#     def get(self, request, format=None):
#         books = Book.objects.all()
#         print(books)
#         serializer = BookSerializer(books, many=True)
#         print(serializer.data)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

# class BookRest(APIView):

#     def get_object(self, pk):
#         try:
#             return Book.objects.get(id=pk)
#         except Book.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         """Retrieve a particular book"""
#         book = self.get_object(pk)

#         serializer = BookSerializer(book)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         book = self.get_object(pk)
#         serializer = BookSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, pk, format=None):
#         book = self.get_object(pk)
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)