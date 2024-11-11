# verification/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('verify/', views.verify_certificate, name='verify_certificate'),
]
