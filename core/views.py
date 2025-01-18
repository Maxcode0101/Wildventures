from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import Campervan  # Import Campervan
from booking.models import Booking  # Import Booking

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
    max_price = request.GET.get('max_price', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    campervans = Campervan.objects.all()

    # Filter by search query
    if query:
        campervans = campervans.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Filter by brand
    if selected_brand:
        campervans = campervans.filter(brand=selected_brand)

    # Filter by model
    if selected_model:
        campervans = campervans.filter(model=selected_model)

    # Filter by capacity
    if selected_capacity.isdigit():
        campervans = campervans.filter(capacity__gte=int(selected_capacity))

    # Filter by maximum price
    if max_price.isdigit():
        campervans = campervans.filter(price_per_day__lte=int(max_price))

    # Global availability filter
    if start_date and end_date:
        unavailable_ids = Booking.objects.filter(
            start_date__lt=end_date,
            end_date__gt=start_date
        ).values_list('campervan_id', flat=True)
        campervans = campervans.exclude(id__in=unavailable_ids)

    # Get distinct brands and models for the filters
    brands = Campervan.objects.values_list('brand', flat=True).distinct().order_by('brand')
    models = (
        Campervan.objects.filter(brand=selected_brand)
        .values_list('model', flat=True)
        .distinct()
        .order_by('model') if selected_brand else Campervan.objects.values_list('model', flat=True).distinct().order_by('model')
    )

    capacity_range = range(1, 11)

    # Pagination
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
        'selected_capacity': selected_capacity,
        'max_price': max_price,
        'capacity_range': capacity_range,
        'start_date': start_date,
        'end_date': end_date,
    })

def check_availability(request):
    """View to check campervan availability for selected dates."""
    campervan_id = request.GET.get('campervan_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Validate input
    if not (campervan_id and start_date and end_date):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    try:
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            campervan_id=campervan_id,
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        is_available = not overlapping_bookings.exists()
        return JsonResponse({'is_available': is_available})
    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({'error': str(e)}, status=500)
