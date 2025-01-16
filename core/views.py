from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import Campervan
from django.db.models import Q


# Create your views here.

def about(request):
    """View to display the About page."""
    return render(request, 'core/about.html')

def contact(request):
    """Display the Contact page."""
    return render(request, 'core/contact.html')

def campervan_list(request):
    query = request.GET.get('q', '').strip()  # Search query
    selected_brand = request.GET.get('brand', '')
    selected_model = request.GET.get('model', '')
    selected_capacity = request.GET.get('capacity', '')

    # Filter campervans (brand, model, capacity and search)
    campervans = Campervan.objects.all()

    if query:
        campervans = campervans.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if selected_brand:
        campervans = campervans.filter(brand=selected_brand)
    if selected_model:
        campervans = campervans.filter(model=selected_model)
    if selected_capacity:
        campervans = campervans.filter(capacity__gte=selected_capacity)  # Filter by capacity greater than or equal

    # Populate dropdown data
    brands = Campervan.objects.values_list('brand', flat=True).distinct().order_by('brand')
    models = (
        Campervan.objects.filter(brand=selected_brand)
        .values_list('model', flat=True)
        .distinct()
        .order_by('model')
        if selected_brand
        else Campervan.objects.values_list('model', flat=True).distinct().order_by('model')
    )
    capacities = Campervan.objects.values_list('capacity', flat=True).distinct().order_by('capacity')

    # Pagination logic
    paginator = Paginator(campervans, 5)  # Show 5 campervans per page
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
        'capacities': capacities,
        'selected_brand': selected_brand,
        'selected_model': selected_model,
        'selected_capacity': selected_capacity,
    })