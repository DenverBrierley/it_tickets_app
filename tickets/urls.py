from django.urls import path
from . import views

# These URL patterns set out the structure and URLs for the app.
# All URLs are formed in the path() function with 3 arguments:
# The URL route defines the location of the view in the site structure.
# The view that is used to load the required data and apply logic to the page is called.
# The URL is named.
urlpatterns = [
    path("", views.home, name="home"),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('tickets/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('tickets/<int:ticket_id>/update/', views.ticket_update_view, name='ticket_update'),
    path('tickets/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
    path('forbidden/', views.forbidden_view, name='forbidden'),
]