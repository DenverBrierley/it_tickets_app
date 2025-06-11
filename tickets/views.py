import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Tickets, Comment
from .forms import TicketForm, CustomUserCreationForm, CommentForm
from django.http import HttpResponseForbidden

# define the logger for error logging
logger = logging.getLogger(__name__)

# Function to check if user is an admin
def is_admin(user):
    return user.is_staff

# Homepage
def home(request):
    #renders the homepage template
    return render(request, 'tickets/home.html')

# User Registration
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        # If the details entered on the form is valid it wil POST the user details to the database, log the user in
        # and take them back to the homepage
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
        # If the form is invalid then it will reject the registration
        else:
            # Log failed registration due to invalid form
            logger.warning("Registration form was invalid.")
            messages.error(request, 'Registration unsuccessful. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    # This renders the webpage and form
    return render(request, 'registration/register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        # If the data provided is valid then the program will authenticate the user details
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            # If the user isn't logged in then they will be logged in and directed to the ticket list
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('ticket_list')
            # Provides error message for incorrect details
            else:
                # Log failed login attempt
                logger.warning(f"Invalid login attempt for username: '{username}'.")
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    # This renders the webpage and form
    return render(request, 'registration/login.html', {'form': form})

# User Logout
@login_required
def logout_view(request):
    # When the users clicks 'logout' a verification message will appear and they will be
    # sent to the homepage
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# Ticket List View
@login_required # User has to be logged in to see this
def ticket_list_view(request):
    # Show all tickets in the database as objects ordered by ticket ID
    tickets = Tickets.objects.all().order_by('-ticket_id') # Show newest first
    # render page and tickets
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

# Ticket Detail View
@login_required
def ticket_detail_view(request, ticket_id):
    # Gets the ticket object (or error) and all comments related to the ticket
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)
    comments = ticket.comments.all()

    if request.method == 'POST':
        # When a user adds a comment using the form it will save:
        # the comment text, the user and its associated ticket
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.ticket = ticket
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Your comment has been added successfully.')
            #Redirects back to the ticket page
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            # comment error message and log
            logger.warning(f"Invalid comment form by '{request.user.username}' on ticket id={ticket_id}.")
            messages.error(request, 'There was an error submitting your comment.')
    else:
        comment_form = CommentForm()

    # Prepare the context dictionary to pass data to the template
    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    }
    # renders page and context dictionary
    return render(request, 'tickets/ticket_detail.html', context)

# Create Ticket View
@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        # Loads the client creation form and checks if the entries are valid before saving the data
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            # Redirects to the newly created ticket
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            # Error message and log
            logger.warning(f"User '{request.user.username}' failed to create a ticket due to invalid form.")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TicketForm()
        # renders the webpage and form
    return render(request, 'tickets/ticket_form.html', {'form': form})

# Update Ticket View
@login_required
def ticket_update_view(request, ticket_id):
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)

    if request.method == 'POST':
        # Populate the form with the existing ticket instance and new POST data
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            # error message and log
            logger.warning(f"Invalid form submission by '{request.user.username}' for ticket update id={ticket_id}.")
            messages.error(request, 'Please correct the errors below.')
    else:
        # Populate the form with the existing ticket instance data
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'ticket': ticket})

# Delete Ticket View (Admin only)
@login_required
@user_passes_test(is_admin, login_url='/tickets/forbidden/') # Redirect if not admin
def ticket_delete_view(request, ticket_id):
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)
    if request.method == 'POST':
        ticket_title = ticket.title
        #deletes ticket
        ticket.delete()
        # success message
        messages.success(request, f'Ticket "{ticket_title}" deleted successfully!')
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})

@login_required
# Renders page for forbidden request
def forbidden_view(request):
    logger.warning(f"User '{request.user.username}' was denied access and redirected to forbidden page.") # logs error
    return render(request, 'tickets/forbidden.html')