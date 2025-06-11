from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Tickets, Comment
from .forms import TicketForm, CommentForm


class TicketAppTests(TestCase):

    # Set up initial data for tests, including two users (one staff) and a ticket.
    def setUp(self):
        self.client = Client()
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='password123',
            email='admin@example.com'
        )
        # Create a ticket instance for testing
        self.ticket = Tickets.objects.create(
            title='Test Ticket',
            description='This is a test description.',
            severity=3,
            status='Open'
        )

    # Model Tests

    def test_ticket_model_creation(self):
        # Test if the ticket was created correctly in setUp.
        self.assertEqual(self.ticket.title, 'Test Ticket')
        self.assertEqual(self.ticket.severity, 3)
        self.assertEqual(str(self.ticket), 'Test Ticket')

    def test_comment_model_creation(self):
        # Test the creation of a Comment object.
        comment = Comment.objects.create(
            ticket=self.ticket,
            user=self.user,
            text='This is a test comment.'
        )
        self.assertEqual(comment.text, 'This is a test comment.')
        self.assertEqual(comment.ticket.title, 'Test Ticket')
        self.assertEqual(comment.user.username, 'testuser')
        self.assertEqual(str(comment), f"Comment by {self.user.username} on Ticket {self.ticket.ticket_id}")

    # Form Tests

    def test_ticket_form_valid(self):
        # Test if the TicketForm is valid with correct data.
        form = TicketForm(data={
            'title': 'Form Test Ticket',
            'description': 'A description from a form.',
            'severity': 2,
            'status': 'In Progress'
        })
        self.assertTrue(form.is_valid())

    def test_ticket_form_invalid(self):
        # Test if the TicketForm is invalid with missing data.
        form = TicketForm(data={'title': 'Missing fields'})
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)  # Check for specific field error

    def test_comment_form_valid(self):
        # Test if the CommentForm is valid with correct data.
        form = CommentForm(data={'text': 'A valid comment.'})
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid(self):
        # Test if the CommentForm is invalid with no data.
        form = CommentForm(data={'text': ''})
        self.assertFalse(form.is_valid())

    # View and URL Tests

    def test_home_view(self):
        # Test the home page accessibility.
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/home.html')

    def test_login_required_for_ticket_list(self):
        # Test if ticket list redirects to login when not authenticated.
        response = self.client.get(reverse('ticket_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('ticket_list')}")

    def test_ticket_list_view_for_logged_in_user(self):
        # Test if the ticket list is accessible to a logged-in user.
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('ticket_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_list.html')
        self.assertContains(response, self.ticket.title)

    def test_ticket_detail_view(self):
        # Test if the ticket detail page is accessible and shows comments.
        self.client.login(username='testuser', password='password123')
        Comment.objects.create(ticket=self.ticket, user=self.user, text='My test comment')
        response = self.client.get(reverse('ticket_detail', args=[self.ticket.ticket_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ticket.title)
        self.assertContains(response, 'My test comment')

    def test_ticket_create_view(self):
        # Test the creation of a new ticket via the form.
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('ticket_create'), {
            'title': 'New Ticket from Test',
            'description': 'Functional test creation.',
            'severity': 4,
            'status': 'Open'
        }, follow=True)  # Follow the redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ticket created successfully!')
        self.assertTrue(Tickets.objects.filter(title='New Ticket from Test').exists())

    def test_ticket_update_view(self):
        # Test updating an existing ticket.
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('ticket_update', args=[self.ticket.ticket_id]), {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'severity': 1,
            'status': 'Resolved'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ticket updated successfully!')
        self.ticket.refresh_from_db()  # Refresh the object from the database
        self.assertEqual(self.ticket.title, 'Updated Title')
        self.assertEqual(self.ticket.status, 'Resolved')

    # Authorization Tests

    def test_user_cannot_delete_ticket(self):
        # Ensure a non-admin user cannot delete a ticket.
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('ticket_delete', args=[self.ticket.ticket_id]))
        # User should be redirected to the 'forbidden' page.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forbidden'))
        # Ensure the ticket still exists
        self.assertTrue(Tickets.objects.filter(pk=self.ticket.ticket_id).exists())

    def test_admin_can_delete_ticket(self):
        # Ensure an admin user can delete a ticket.
        self.client.login(username='adminuser', password='password123')
        # GET the confirmation page first
        response_get = self.client.get(reverse('ticket_delete', args=[self.ticket.ticket_id]))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'tickets/ticket_confirm_delete.html')
        # POST to confirm deletion
        response_post = self.client.post(reverse('ticket_delete', args=[self.ticket.ticket_id]), follow=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertContains(response_post, f'Ticket "{self.ticket.title}" deleted successfully!')
        # Ensure the ticket no longer exists
        self.assertFalse(Tickets.objects.filter(pk=self.ticket.ticket_id).exists())


