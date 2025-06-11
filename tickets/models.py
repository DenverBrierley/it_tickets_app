from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Creates a database table for tickets to be stored in.
class Tickets(models.Model):
    # Primary field for tickets IDs that increments with every new entry
    ticket_id = models.AutoField(primary_key=True)
    # Ticket title character field with a maximum length of 100 characters
    title = models.CharField(max_length=100)
    # Standard text field for ticket description
    description = models.TextField()
    # Integer field to mark the incident's severity
    severity = models.IntegerField()
    # Character field with maximum length of 50 for the ticket's status
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.title

# Creates a database table for comments to be stored in.
class Comment(models.Model):
    # Primary field for comment IDs that increments with every new entry
    comment_id = models.AutoField(primary_key=True)
    # Foreign Key to assign a comment to a ticket
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name='comments')
    # Foreign key to Django's users table to assign the comment to a user
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    # Standard text field for comment content
    text = models.TextField()
    # Comment timestamp
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username if self.user else 'Unknown'} on Ticket {self.ticket.ticket_id}"

    class Meta:
        # Show oldest comments first
        ordering = ['created_at']