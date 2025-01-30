from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import Campervan, Booking, BookingChangeRequest
from datetime import datetime


@login_required
def book_campervan(request, campervan_id):
    """
    Responsible for campervan bookings. 
    Populates booking dates passed from the availability check.
    Overrides GET-data with POST-data.
    """
    campervan = get_object_or_404(Campervan, id=campervan_id)
    start_date_str = request.GET.get('start_date', '') or request.POST.get('start_date', '')
    end_date_str = request.GET.get('end_date', '') or request.POST.get('end_date', '')

    if request.method == 'POST':
        try:
            start_date_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'Invalid date format.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Ensure end_date < start_date
        if end_date_dt <= start_date_dt:
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'End date must be after the start date.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date_dt,
            end_date__gt=start_date_dt
        )
        if overlapping_bookings.exists():
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'The campervan is not available for the selected dates.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Creates booking
        booking = Booking.objects.create(
            campervan=campervan,
            user=request.user,
            start_date=start_date_dt,
            end_date=end_date_dt,
            total_price=(end_date_dt - start_date_dt).days * campervan.price_per_day
        )

        # Send confirmation email and redirect to campervans
        send_booking_confirmation_email(booking)
        return redirect('campervan_list')

    # GET request: Show form
    return render(request, 'booking/book_campervan.html', {
        'campervan': campervan,
        'start_date': start_date_str,
        'end_date': end_date_str,
    })


@login_required
def booking_confirmation(request, booking_id):
    """
    Shows booking confirmation
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    return render(request, 'booking/booking_confirmation.html', {
        'booking': booking,
    })


def check_availability(request):
    """
    Responsible for availability checks
    """
    campervan_id = request.GET.get('campervan_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    try:
        campervan = Campervan.objects.get(id=campervan_id)
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        overlapping_bookings = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date,
            end_date__gt=start_date
        )
        is_available = not overlapping_bookings.exists()
        return JsonResponse({'is_available': is_available})

    except (Campervan.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalid data provided.'}, status=400)


@login_required
def check_booking_status(request, booking_id):
    """
    Function to check the booking status (pending, confirmed, canceled)
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return JsonResponse({'status': booking.status})


@login_required
def cancel_booking(request, booking_id):
    """
    Cancel booking with confirmation on the site or redirection to my bookings page.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'Cancelled':
        messages.error(request, "This booking is already canceled.", extra_tags="my_bookings")
        return redirect('my_bookings')

    # Update booking status
    booking.status = 'Cancelled'
    booking.save()

    # Send cancellation email
    send_cancellation_email(booking)

    # Cancelation confirmation
    messages.success(request, "Your booking has been canceled successfully!", extra_tags="my_bookings")

    # Redirect user to my bookings page
    return redirect('my_bookings')



def send_booking_confirmation_email(booking):
    """
    Sends confirmation email on sucessfull bookings
    """
    subject = 'Booking Confirmation'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} is confirmed.\n"
        f"Start Date: {booking.start_date}\n"
        f"End Date: {booking.end_date}\n"
        f"Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for choosing Us!\n\n"
        f"Best regards\n\n"
        f"Your Wildventures Team"
    )
    recipient_list = [booking.user.email]
    send_mail(subject, message, 'no-reply@wildventures.com', recipient_list, fail_silently=True)


def send_cancellation_email(booking):
    """
    Sends confirmation email on canceled bookings
    """
    subject = 'Booking Cancellation'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} from {booking.start_date} to {booking.end_date} for ${booking.total_price:.2f} has been canceled.\n"
        f"Thank you for your visit, we hope to see you soon again.\n\n"
        f"Best regards\n\n"
        f"Your Wildventures Team"
    )
    recipient_list = [booking.user.email]
    send_mail(subject, message, 'no-reply@wildventures.com', recipient_list, fail_silently=True)


@login_required
def my_bookings(request):
    """
    View to display all bookings for the logged-in user.
    """
    bookings = Booking.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})


@login_required
def booking_details(request, booking_id):
    """
    Displays detailed info about a single booking.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_details.html', {
        'booking': booking,
    })

@login_required
def edit_booking(request, booking_id):
    """
    Date change self service for pending bookings.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'Pending':
        messages.error(request, "Self service is only available for pending bookings, please contact the customer service.")
        return redirect('my_bookings')

    if request.method == "POST":
        new_start = request.POST.get("start_date")
        new_end = request.POST.get("end_date")

        try:
            new_start_dt = datetime.strptime(new_start, "%Y-%m-%d").date()
            new_end_dt = datetime.strptime(new_end, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('edit_booking', booking_id=booking_id)

        # Validation of new dates
        if new_end_dt <= new_start_dt:
            messages.error(request, "Invalid input. End date must be after start date.")
            return redirect('edit_booking', booking_id=booking_id)

        # Prevent overlapping booking
        overlapping = Booking.objects.filter(
            campervan=booking.campervan,
            start_date__lt=new_end_dt,
            end_date__gt=new_start_dt
        ).exclude(id=booking.id)
        if overlapping.exists():
            messages.error(request, "This campervan is not available for the requested dates")
            return redirect('edit_booking', booking_id=booking_id)

        # Update the booking
        booking.start_date = new_start_dt
        booking.end_date = new_end_dt
        booking.total_price = (new_end_dt - new_start_dt).days * booking.campervan.price_per_day
        booking.save()

        messages.success(request, "We sucessfully changed your booking!")
        return redirect('my_bookings')

    # Get request: Display new booking details
    return render(request, 'booking/edit_booking.html', {
        'booking': booking,
    })


@login_required
def request_date_change(request, booking_id):
    """
    User can suggest date change for confirmed booking. 
    Needs admin aproval
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != 'Confirmed':
        messages.error(request, "Date change requests are only available for confirmed bookings - use self service for pending bookings instead.")
        return redirect('my_bookings')

    if request.method == "POST":
        new_start = request.POST.get("start_date")
        new_end = request.POST.get("end_date")

        try:
            new_start_dt = datetime.strptime(new_start, "%Y-%m-%d").date()
            new_end_dt = datetime.strptime(new_end, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('request_date_change', booking_id=booking_id)

        if new_end_dt <= new_start_dt:
            messages.error(request, "End date must be after start date.")
            return redirect('request_date_change', booking_id=booking_id)

        bcr = BookingChangeRequest.objects.create(
            booking=booking,
            requested_start_date=new_start_dt,
            requested_end_date=new_end_dt,
        )

        messages.success(request, "Your request has been submitted to our team for approval")
        return redirect('my_bookings')

    # GET request
    return render(request, 'booking/request_date_change.html', {
        'booking': booking,
    })