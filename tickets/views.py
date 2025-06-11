from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Tickets, Comment
from .forms import TicketForm, CustomUserCreationForm, CommentForm
from django.http import HttpResponseForbidden

# Helper function to check if user is admin (staff)
def is_admin(user):
    return user.is_staff

# Home View (existing, slightly modified for context)
def home(request):
    return render(request, 'tickets/home.html')

# User Registration
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home') # Or 'ticket_list'
        else:
            messages.error(request, 'Registration unsuccessful. Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# User Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('ticket_list') # Redirect to a relevant page
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# User Logout
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# Ticket List View
@login_required
def ticket_list_view(request):
    tickets = Tickets.objects.all().order_by('-ticket_id') # Show newest first
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

# Ticket Detail View
@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)
    comments = ticket.comments.all() # Get all comments related to the ticket

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.ticket = ticket
            new_comment.user = request.user
            new_comment.save()
            messages.success(request, 'Your comment has been added successfully.')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, 'There was an error submitting your comment.')
    else:
        comment_form = CommentForm() # An empty form for GET requests

    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tickets/ticket_detail.html', context)

# Create Ticket View
@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.save()
            messages.success(request, 'Ticket created successfully!')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})

# Update Ticket View
@login_required
def ticket_update_view(request, ticket_id):
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully!')
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TicketForm(instance=ticket)
    return render(request, 'tickets/ticket_form.html', {'form': form, 'ticket': ticket})

# Delete Ticket View (Admin only)
@login_required
@user_passes_test(is_admin, login_url='/tickets/forbidden/') # Redirect if not admin
def ticket_delete_view(request, ticket_id):
    ticket = get_object_or_404(Tickets, ticket_id=ticket_id)
    if request.method == 'POST':
        ticket_title = ticket.title # For message
        ticket.delete()
        messages.success(request, f'Ticket "{ticket_title}" deleted successfully!')
        return redirect('ticket_list')
    return render(request, 'tickets/ticket_confirm_delete.html', {'ticket': ticket})

@login_required
def forbidden_view(request):
    return render(request, 'tickets/forbidden.html') # Create this simple template