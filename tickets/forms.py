from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tickets, Comment

# User registration form that extends Django's default Form
class CustomUserCreationForm(UserCreationForm):
    # Inner Meta class to configure the form
    class Meta(UserCreationForm.Meta):
        # Specifies the model this form is for
        model = User
        # Specifies the fields to include, inheriting from the base form and adding more
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

# Form for creating and updating tickets
class TicketForm(forms.ModelForm):
    # Defines choices for the severity field to create a dropdown menu
    SEVERITY_CHOICES = [
        (1, '1 - Critical'),
        (2, '2 - High'),
        (3, '3 - Medium'),
        (4, '4 - Low'),
    ]
    # Defines choices for the status field
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    # Overrides the default integer field with a choice field using a dropdown menu
    severity = forms.ChoiceField(choices=SEVERITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    # Overrides the default char field with a dropdown menu
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    # Overrides the default text field to use a larger text field
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}))
    # Applies a CSS class to the title input field
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Tickets
        # Specifies the fields from the model to include in the form
        fields = ['title', 'description', 'severity', 'status']

# Form for creating new comments
class CommentForm(forms.ModelForm):
    # Overrides the default text field for more control over its appearance
    text = forms.CharField(
        # Use a Text field with a specific size and placeholder text
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your comment...'}),
        label=""
    )

    class Meta:
        model = Comment
        # Specifies the fields from the model to include in the form
        fields = ['text']
