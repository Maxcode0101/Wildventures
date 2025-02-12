
import json
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import datetime
from .models import Campervan  # Import Campervan
from booking.models import Booking  # Import Booking
from .forms import ContactForm


# Create your views here.

def about(request):
    """View to display the About page."""
    return render(request, 'core/about.html')

def contact(request):
    """Display the Contact page and handle form."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Extract form data
            name = form.cleaned_data["name"]
            user_email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            
            # Prepare email subject and body
            email_subject = f"Contact Form: {subject}"
            email_body = (
                f"Name: {name}\n"
                f"Email: {user_email}\n"
                f"Subject: {subject}\n"
                f"Message:\n{message}"
            )
            
            # Define the sender email and recipient list
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.DEFAULT_ADMIN_EMAIL]
            
            # Send email
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )

            messages.success(request, "The message has been sent. We'll get back at you soon!")
            return redirect("contact")
        
        else:
            messages.error(request, "Please correct the invalid fields.")
            
    else:
        form = ContactForm()            
    return render(request, 'core/contact.html', {"form": form})

def faq(request):
    """Display the FAQ page."""
    return render(request, 'core/faq.html')

def campervan_list(request):
    query = request.GET.get('q', '').strip()
    selected_brand = request.GET.get('brand', '').strip()
    selected_model = request.GET.get('model', '').strip()
    selected_capacity = request.GET.get('capacity', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    campervans = Campervan.objects.all()

    # Apply filters to the main QuerySet.
    if query:
        campervans = campervans.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if selected_brand:
        campervans = campervans.filter(brand__iexact=selected_brand)
    if selected_model:
        campervans = campervans.filter(model__iexact=selected_model)
    if selected_capacity.isdigit():
        campervans = campervans.filter(capacity__gte=int(selected_capacity))
    if max_price.isdigit():
        campervans = campervans.filter(price_per_day__lte=int(max_price))
    if start_date and end_date:
        unavailable_ids = Booking.objects.filter(
            start_date__lt=end_date,
            end_date__gt=start_date
        ).values_list('campervan_id', flat=True)
        campervans = campervans.exclude(id__in=unavailable_ids)

    # Build full dropdown lists for filtering from the full dataset
    brands_list = list(
        Campervan.objects.exclude(brand__isnull=True).values_list('brand', flat=True).distinct().order_by('brand')
    )
    models_list = list(
        Campervan.objects.exclude(model__isnull=True).values_list('model', flat=True).distinct().order_by('model')
    )

    # Build mappings for dynamic filtering.
    brand_models_mapping = {}
    for brand in Campervan.objects.exclude(brand__isnull=True).values_list('brand', flat=True).distinct():
        brand_models = list(
            Campervan.objects.filter(brand__iexact=brand).exclude(model__isnull=True)
            .values_list('model', flat=True).distinct().order_by('model')
        )
        brand_models_mapping[brand] = brand_models

    model_brands_mapping = {}
    for model in Campervan.objects.exclude(model__isnull=True).values_list('model', flat=True).distinct():
        model_brands = list(
            Campervan.objects.filter(model__iexact=model).exclude(brand__isnull=True)
            .values_list('brand', flat=True).distinct().order_by('brand')
        )
        model_brands_mapping[model] = model_brands

    # Build full dataset for client‑side filtering (for capacity and for rebuilding full lists)
    campers_data = list(Campervan.objects.all().values('brand', 'model', 'capacity'))

    # Serialize JSON strings.
    brand_models_json = json.dumps(brand_models_mapping)
    model_brands_json = json.dumps(model_brands_mapping)
    brands_json = json.dumps(brands_list)
    models_json = json.dumps(models_list)
    campers_data_json = json.dumps(campers_data)

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
        'brands': brands_list,
        'models': models_list,
        'selected_brand': selected_brand,
        'selected_model': selected_model,
        'selected_capacity': selected_capacity,
        'max_price': max_price,
        'capacity_range': capacity_range,
        'start_date': start_date,
        'end_date': end_date,
        'brand_models_json': brand_models_json,
        'model_brands_json': model_brands_json,
        'brands_json': brands_json,
        'models_json': models_json,
        'campers_data_json': campers_data_json,
    })

def check_availability(request):
    """View to check campervan availability for selected dates."""
    campervan_id = request.GET.get('campervan_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    try:
        # Check if start_date < end_date
        campervan = Campervan.objects.get(id=campervan_id)
        start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        if end_date_dt <= start_date_dt:
            return JsonResponse({'Invalid input': 'End date must be after start date'}, status=400)

        overlapping_bookings = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date_dt,
            end_date__gt=start_date_dt
        )
        is_available = not overlapping_bookings.exists()
        return JsonResponse({'is_available': is_available})

    except (Campervan.DoesNotExist, ValueError):
        # Handle unexpected errors
        return JsonResponse({'error': 'An unexcepted error occured'}, status=400)