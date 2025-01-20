from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Campervan
from .models import Booking
from .forms import BookingForm  # Booking form

@login_required
def book_campervan(request, campervan_id):
    """View to handle campervan booking."""
    campervan = get_object_or_404(Campervan, id=campervan_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                campervan=campervan,
                start_date__lt=end_date,
                end_date__gt=start_date,
            )
            if overlapping_bookings.exists():
                messages.error(request, "The campervan is not available for the selected dates.")
            else:
                # Calculate total price
                days = (end_date - start_date).days
                total_price = days * campervan.price_per_day

                # Save booking
                booking = form.save(commit=False)
                booking.campervan = campervan
                booking.user = request.user
                booking.total_price = total_price
                booking.status = 'Pending'  # Default status
                booking.save()

                messages.success(request, "Booking request has been sent successfully!")
                return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'booking/book_campervan.html', {
        'campervan': campervan,
        'form': form
    })

@login_required
def booking_confirmation(request, booking_id):
    """View to display booking confirmation."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_confirmation.html', {
        'booking': booking
    })
