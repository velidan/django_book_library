from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required

import datetime

# from catalog.forms import RenewBookForm, CreateBookForm
from catalog.forms import RenewBookForm

# generic CRUD
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalog.models import Author, Book


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
     # By default, these views will redirect on success to a page displaying the newly created/edited model item
    model = Book
    fields = '__all__'

    # custom success url to redirect after the form proceed
    # success_url = reverse_lazy('books')

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

# working - book create 

# def bookCreate(request):
#     """ function based create view """

#     form = None

#     if request.method == 'POST':
#         form = CreateBookForm(request.POST)

#         if form.is_valid():
#             data = form.cleaned_data
#             print(data)
#             b = Book(title=data['title'], summary=data['summary'], isbn=data['isbn'])
#             b.save()
#             b.genre.set(data['genre'])
#             b.author = data['author']
#             b.save()
#             return HttpResponseRedirect(reverse('books'))
#     else:
#         form = CreateBookForm()
        


#     context = {
#         'form': form
#     }

#     return render(request, 'catalog/book_form.html', context)
    



# --- working generic create book Functionality --- 

# class BookCreate(PermissionRequiredMixin, CreateView):
#     # a url guard to allow only librarians to create this book
#     permission_required = 'catalog.can_mark_returned'

#     model = Book
#     fields = '__all__'



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
    # queryset = Book.objects.all()[:5] # get 5 books containing the title book
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