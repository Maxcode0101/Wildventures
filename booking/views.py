from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Campervan
from booking.models import Booking
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta, date

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

        # Check for availability and overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        if overlapping_bookings.exists():
            messages.error(request, "The campervan is not available for the selected dates.")
            return redirect("book_campervan", campervan_id=campervan_id)

        # Shows the total booking costs
        days = (end_date - start_date).days
        total_price = days * campervan.price_per_day

        # Creates a booking
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


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, "booking/booking_confirmation.html", {
        "booking": booking,
        "user": request.user,
    })


@login_required
def my_bookings(request):
    """View to display user's bookings."""
    bookings = Booking.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})


@login_required
def booking_details(request, booking_id):
    """View to display details of a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  # Ensure user owns the booking
    return render(request, 'booking/booking_details.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    # Fetch the booking object
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if the booking is already canceled
    if booking.status == "Canceled":
        messages.error(request, "This booking has already been canceled.", extra_tags="my_bookings")
        return redirect("my_bookings")

    # Prevent cancelations of past bookings
    if booking.end_date < date.today():
        messages.error(request, "You cannot cancel a booking that has already ended.", extra_tags="my_bookings")
        return redirect("my_bookings")

    # Update status to "Canceled"
    booking.status = "Canceled"
    booking.save()

    # Provides feedback to the user when canceling a booking
    messages.success(request, "Your booking has been successfully canceled, a confirmation email has been sent!", extra_tags="my_bookings")

    # Email notifications for admin and user on cancelations
    admin_email = settings.DEFAULT_ADMIN_EMAIL
    user_email = request.user.email
    subject = f"Booking Canceled: {booking.campervan.name}"
    message = f"""
    Dear {request.user.username},

    Your booking for {booking.campervan.name} from {booking.start_date} to {booking.end_date} has been canceled.

    Thank you for your visit, we hope to see you soon again.

    Best Regards,
    Your Campervan Rental Team
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email, user_email],  # Sends email to admin and user
            fail_silently=False,  # Raise errors if sending fails
        )
        messages.success(request, "A confirmation email has been sent.")
    except Exception as e:
        messages.error(request, f"Your booking has been sucessfully canceled, but an error occurred when sending the confirmation email: {str(e)}", extra_tags="my_bookings")

    return redirect("my_bookings")
