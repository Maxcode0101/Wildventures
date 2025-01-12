from django.shortcuts import render

# Create your views here.

def about(request):
    """View to display the About page."""
    return render(request, 'core/about.html')
