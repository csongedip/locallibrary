from django.contrib import admin
from .models import Book, BookInstance, Genre, Author, Language

# Register your models here.

# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
# admin.site.register(Author)
admin.site.register(Language)

# Define the admin class

class BookInline(admin.TabularInline):
    model = Book
    extra = 0

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]

# Register the Admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]


# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ("status", "due_back")
    list_display = ('book', 'id', 'status', 'borrower', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'borrower', 'due_back')
        }

        )
    )

