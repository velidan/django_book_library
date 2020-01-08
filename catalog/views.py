from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    context_object_name = 'my_book_list' # own name for the list as a template variable
    queryset = Book.objects.all()[:5] # get 5 books containing the title book
    # queryset = Book.objects.filter(title__icontains='book')[:5] # get 5 books containing the title book
    # template_name = 'books/my_arbitrary_template_name_list.html' # specify your own template name/location

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

class BookDetailView(generic.DetailView):
    model = Book

class AuthorsView(generic.ListView):
    model = Author
    context_object_name = 'authors_list'
    queryset = Author.objects.all()
    template_name = 'catalog/authors.html'


class AuthorDetail(generic.DetailView):
    model = Author