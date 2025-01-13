from django.shortcuts import render
from .models import Campervan


# Create your views here.

def about(request):
    """View to display the About page."""
    return render(request, 'core/about.html')

def contact(request):
    """Display the Contact page."""
    return render(request, 'core/contact.html')

def campervan_list(request):
    campervans = Campervan.objects.all()  # Fetch all campervans
    return render(request, 'core/campervan_list.html', {'campervans': campervans})
