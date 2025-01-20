from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Campervan
from booking.models import Booking
from datetime import datetime, timedelta

@login_required
def book_campervan(request, campervan_id):
    campervan = get_object_or_404(Campervan, id=campervan_id)

    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        # Validate dates
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            if start_date >= end_date:
                messages.error(request, "End date must be after the start date.")
                return redirect("book_campervan", campervan_id=campervan_id)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("book_campervan", campervan_id=campervan_id)

        # Check availability
        overlapping_bookings = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        if overlapping_bookings.exists():
            messages.error(request, "The campervan is not available for the selected dates.")
            return redirect("book_campervan", campervan_id=campervan_id)

        # Calculate total price
        days = (end_date - start_date).days
        total_price = days * campervan.price_per_day

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            campervan=campervan,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status="Pending",
        )

        messages.success(request, "Booking successful!")
        return redirect("booking_confirmation", booking_id=booking.id)

    # Handle GET request
    return render(request, "booking/book_campervan.html", {
        "campervan": campervan,
        "start_date": request.GET.get("start_date", ""),
        "end_date": request.GET.get("end_date", ""),
        "total_price": None,  # Calculate on POST
    })
