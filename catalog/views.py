from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Create your views here.

from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the majn objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_book_of_god = Book.objects.filter(title__icontains='ISTEN').count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    num_genres = Genre.objects.count()

    context = {
        'num_books': num_books,
        'num_instances' : num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_book_of_god': num_book_of_god,
        'num_visits': num_visits,
    }

    # Render the HTML templates index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views.generic import ListView, DetailView

class BookListView(ListView):
    model = Book
    template_name = 'book/book_list.html'
    paginate_by = 10

class BookDetailView(DetailView):
    model = Book
    template_name = 'book/book_detail.html'

class AuthorListView(ListView):
    model = Author
    template_name = 'author/author_list.html'
    paginate_by = 10

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'author/author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='authorized/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllBorrowedListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    template_name = 'authorized/lib_all_borrowed.html'
    permission_required = 'catalog.can_mark_returned'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'authorized/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    template_name = 'author/author_form.html'
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    template_name = 'author/author_form.html'
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'author/author_confirm_delete.html'
    permission_required = 'catalog.can_mark_returned'

class BookCreate(PermissionRequiredMixin,CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    # initial = {}
    template_name = 'book/book_form.html'
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    template_name = 'book/book_form.html'
    permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin,DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'book/book_confirm_delete.html'
    permission_required = 'catalog.can_mark_returned'