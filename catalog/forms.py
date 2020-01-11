from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime

from catalog.models import BookInstance, Book, Author, Genre, Language


#  ModelForm Create book - Working
# class CreateBookForm(ModelForm):
#     class Meta:
#         model = Book
#         fields = '__all__'

#     def clean_title(self):
#         title = self.cleaned_data['title']

#         if len(title) < 2:
#             raise ValidationError(_('title should contain more than 2 chars'))
#         return title

# django.Forms based CreateBookForm - working

# class CreateBookForm(forms.Form):
#     title = forms.CharField(help_text="A Book title")
#     author = forms.ModelChoiceField(queryset=Author.objects.all(), help_text='Select a book author')
#     summary = forms.CharField(widget=forms.Textarea, help_text='A Summary of the book')
#     isbn = forms.CharField(help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

#     genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), help_text='Select book genres')
#     language = forms.ModelChoiceField(queryset=Language.objects.all(), help_text='Choose a book language')

#     def clean_title(self):
#         title = self.cleaned_data['title']

#         if len(title) < 2:
#             raise ValidationError(_('title should contain more than 2 chars'))
#         return title

# model form
class RenewBookForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']
       
       # Check if a date is not in the past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       # Check if a date is in the allowed range (+4 weeks from today).
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')} 

# form based
# class RenewBookForm(forms.Form):
#     renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3). YYYY-MM-DD.")

#     def clean_renewal_date(self):
#         data = self.cleaned_data['renewal_date']

#         # Check if a date is not in the past.
#         if data < datetime.date.today():
#             raise ValidationError(_('Invalid date - renewal in past'))

#         # Check if date is in the allowed range (+4 weeks from today).
#         if data > datetime.date.today() + datetime.timedelta(weeks=4):
#             raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

#         # Remember to always return the cleaned data
#         return data