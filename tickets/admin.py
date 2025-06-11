from django.contrib import admin

from django.contrib import admin
from .models import Tickets, Comment

admin.site.register(Tickets)
admin.site.register(Comment)
# Connects the models to the admin panel so admins can perform CRUD within the panel itself.