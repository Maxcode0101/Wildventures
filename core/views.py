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
    query = request.GET.get('q', '').strip()  # Get the search query from the request
    if query:
        campervans = Campervan.objects.filter(
            name__icontains=query  # Filter by name (case-insensitive)
        ) | Campervan.objects.filter(
            description__icontains=query  # Or filter by description (case-insensitive)
        )
    else:
        campervans = Campervan.objects.all()  # Show all campervans if no query

    return render(request, 'core/campervan_list.html', {'campervans': campervans, 'query': query})
