from django.shortcuts import render

# Create your views here.
# certificates/views.py (or your chosen app's views.py)
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
