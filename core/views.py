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
    query = request.GET.get('q', '').strip()  # Get the search query from the request
    brand_filter = request.GET.get('brand', '').strip()  # Filter by brand
    model_filter = request.GET.get('model', '').strip()  # Filter by model

    campervans = Campervan.objects.all()  # Start with all campervans

    # Apply search filter (if query exists)
    if query:
        campervans = campervans.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query)
        )

    # Apply brand filter (if selected)
    if brand_filter:
        campervans = campervans.filter(brand__iexact=brand_filter)

    # Apply model filter (if selected)
    if model_filter:
        campervans = campervans.filter(model__iexact=model_filter)

    # Pagination logic
    paginator = Paginator(campervans, 5)  # Show 5 campervans per page
    page = request.GET.get('page', 1)

    try:
        campervans = paginator.page(page)
    except PageNotAnInteger:
        campervans = paginator.page(1)
    except EmptyPage:
        campervans = paginator.page(paginator.num_pages)

    # Get distinct brand and model options for the dropdown filters
    brands = Campervan.objects.values_list('brand', flat=True).distinct()
    models = Campervan.objects.values_list('model', flat=True).distinct()

    # Pass all necessary context to the template
    return render(request, 'core/campervan_list.html', {
        'campervans': campervans,
        'query': query,
        'brands': brands,
        'models': models,
        'selected_brand': brand_filter,
        'selected_model': model_filter,
    })