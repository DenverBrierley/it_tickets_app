from django.db import models

# Create your models here.

class Tickets(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    severity = models.IntegerField()
    status = models.CharField(max_length=50)
