# certificates/urls.py (or your app's urls.py)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page route
    # Add other URLs here for certificates, verification, etc.
]
