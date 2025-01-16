from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    query = request.GET.get('q', '').strip()  # Get the search query
    selected_brand = request.GET.get('brand', '').strip()  # Get selected brand
    selected_model = request.GET.get('model', '').strip()  # Get selected model

    # Filter campervans based on search, brand, and model
    campervans = Campervan.objects.all()

    if query:
        campervans = campervans.filter(
            name__icontains=query
        ) | campervans.filter(
            description__icontains=query
        )
    if selected_brand:
        campervans = campervans.filter(brand=selected_brand)
    if selected_model:
        campervans = campervans.filter(model=selected_model)

    # Extract unique brands and models
    brands = Campervan.objects.values_list('brand', flat=True).distinct().order_by('brand')

    # Filter models based on selected brand
    if selected_brand:
        models = Campervan.objects.filter(brand=selected_brand).values_list('model', flat=True).distinct().order_by('model')
    else:
        models = Campervan.objects.values_list('model', flat=True).distinct().order_by('model')

    # Pagination logic
    paginator = Paginator(campervans, 5)
    page = request.GET.get('page', 1)
    try:
        campervans = paginator.page(page)
    except PageNotAnInteger:
        campervans = paginator.page(1)
    except EmptyPage:
        campervans = paginator.page(paginator.num_pages)

    return render(request, 'core/campervan_list.html', {
        'campervans': campervans,
        'query': query,
        'brands': brands,
        'models': models,
        'selected_brand': selected_brand,
        'selected_model': selected_model,
    })