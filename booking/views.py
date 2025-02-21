from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import logging

from .models import Campervan, Booking, BookingChangeRequest, BookingCancellationRequest

logger = logging.getLogger(__name__)

###############################################
# Views responsible for Bookings / Availability 
###############################################

@login_required
def book_campervan(request, campervan_id):
    """
    Responsible for campervan bookings. 
    Populates booking dates passed from the availability check.
    Decide if GET-data or POST-data.
    """
    campervan = get_object_or_404(Campervan, id=campervan_id)
    start_date_str = request.POST.get('start_date') or request.GET.get('start_date', '')
    end_date_str = request.POST.get('end_date') or request.GET.get('end_date', '')

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

        # Dissallow bookings in the past
        if start_date_dt < date.today():
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'Start date cannot be in the past.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })
        if end_date_dt < date.today():
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'End date cannot be in the past.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Ensure end_date > start_date
        if end_date_dt <= start_date_dt:
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'End date must be after the start date.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date_dt,
            end_date__gt=start_date_dt
        ).exclude(status='Cancelled')
        if overlapping.exists():
            return render(request, 'booking/book_campervan.html', {
                'campervan': campervan,
                'error': 'The campervan is not available for the selected dates.',
                'start_date': start_date_str,
                'end_date': end_date_str,
            })

        # Creates booking with status Pending (i.e. an unpaid reservation)
        days = (end_date_dt - start_date_dt).days
        total_price = days * campervan.price_per_day

        booking = Booking.objects.create(
            campervan=campervan,
            user=request.user,
            start_date=start_date_dt,
            end_date=end_date_dt,
            total_price=total_price,
            status='Pending'
        )

        # Send reservation notification email prompting payment within 3 days
        send_reservation_confirmation_email(booking)
        return redirect('booking_confirmation', booking_id=booking.id)
        
    # GET request: Show form
    return render(request, 'booking/book_campervan.html', {
        'campervan': campervan,
        'start_date': start_date_str,
        'end_date': end_date_str,
    })


@login_required
def booking_confirmation(request, booking_id):
    """
    Shows booking confirmation (or reservation notice).
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_confirmation.html', {
        'booking': booking,
    })


@login_required
def booking_details(request, booking_id):
    """
    Display more detailed info about a specific booking.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/booking_details.html', {
        'booking': booking,
        'today': date.today(),
    })


def check_availability(request):
    """
    Responsible for availability checks.
    """
    campervan_id = request.GET.get('campervan_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not (campervan_id and start_date and end_date):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    try:
        campervan = Campervan.objects.get(id=campervan_id)
        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Ensure end_date > start_date
        if end_date_dt <= start_date_dt:
            return JsonResponse({'error': 'End date must be after start date.'}, status=400)

        overlapping = Booking.objects.filter(
            campervan=campervan,
            start_date__lt=end_date_dt,
            end_date__gt=start_date_dt
        ).exclude(status='Cancelled')
        is_available = not overlapping.exists()
        return JsonResponse({'is_available': is_available})

    except (Campervan.DoesNotExist, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def check_booking_status(request, booking_id):
    """
    Function to check the booking status (Pending, Confirmed, Cancelled).
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return JsonResponse({'status': booking.status})


@login_required
def cancel_booking(request, booking_id):
    """
    Cancel "Pending" bookings (unpaid reservations) with confirmation on the site.
    Cancellations of "Confirmed" bookings need to be approved by staff.
    Prohibit cancellations of bookings which have already started or ended.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'Cancelled':
        messages.error(request, "This booking is already cancelled.", extra_tags="my_bookings")
        return redirect('my_bookings')

    # Prohibit cancellations of bookings which started already or from the past.
    if booking.start_date <= date.today():
        messages.error(request, "This booking has already ended or is ongoing, and can't be cancelled.", extra_tags="my_bookings")
        return redirect('my_bookings')

    # Prohibit self-service cancellations if booking status is Confirmed.
    if booking.status == 'Confirmed':
        messages.error(request, "Cancellation request was sent to admin for approval", extra_tags="my_bookings")
        return redirect('my_bookings')

    booking.status = 'Cancelled'
    booking.save()

    # Send cancellation email.
    send_cancellation_email(booking)
    messages.success(request, "Your booking has been cancelled successfully!", extra_tags="my_bookings")
    return redirect('my_bookings')


###########################
# Checkout / Stripe payment
###########################

@login_required
def create_checkout_session(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Disallow payment if the booking isn't pending (waiting for payment).
    if booking.status != 'Pending':
        return redirect('booking_details', booking_id=booking.id)
    
    # Additional safeguard: Prevent payment if the booking's start date is in the past or today.
    if booking.start_date <= date.today():
        messages.error(request, "You can't process payment for a booking that is ongoing or in the past.", extra_tags="my_bookings")
        return redirect('booking_details', booking_id=booking.id)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount_in_cents = int(booking.total_price * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': f"Booking #{booking.id}",
                },
                'unit_amount': amount_in_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        client_reference_id=str(booking.id),
        metadata={
            'booking_id': str(booking.id)
        }
    )

    return redirect(session.url, code=303)


def payment_success(request):
    return render(request, 'booking/payment_success.html')


def payment_cancel(request):
    return render(request, 'booking/payment_cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature: %s", e)
        return HttpResponse(status=400)

    logger.info("Received event type: %s", event.get('type'))

    # Process only checkout.session.completed events.
    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata', {})
        logger.info("Session metadata: %s", metadata)
        logger.info("Payment status: %s", session.get('payment_status'))

        # Try to retrieve the booking ID from metadata, or fallback to client_reference_id.
        booking_id_str = metadata.get('booking_id') or session.get('client_reference_id')
        if booking_id_str:
            try:
                booking = Booking.objects.get(pk=int(booking_id_str))
                # Update booking status only if currently Pending (waiting for payment).
                if booking.status == 'Pending':
                    booking.status = 'Confirmed'
                    booking.save()
                    # Send final confirmation email after payment is received.
                    send_booking_confirmation_email(booking)
                    logger.info("Booking (id: %s) updated to Confirmed.", booking_id_str)
                else:
                    logger.info("Booking (id: %s) is already updated to %s", booking_id_str, booking.status)
            except Booking.DoesNotExist:
                logger.error("Booking with id %s does not exist.", booking_id_str)
        else:
            logger.error("No booking_id found in session metadata.")
    else:
        logger.info("Unhandled event type: %s", event.get('type'))

    return HttpResponse(status=200)


@login_required
def request_cancellation(request, booking_id):
    """
    Allow a user to request cancellation for a confirmed booking.
    Prohibit cancellation requests if the booking has already started or is in the past.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Block cancellation requests for ongoing or past bookings.
    if booking.start_date <= date.today():
        messages.error(request, "You can't cancel bookings that are ongoing or in the past. Please visit our contact page for assistance.", extra_tags="my_bookings")
        return redirect('my_bookings')

    if booking.status != 'Confirmed':
        messages.error(request, "Cancellation requests can only be made for confirmed bookings.")
        return redirect('my_bookings')

    if booking.cancellation_requests.filter(status='Pending').exists():
        messages.info(request, "Cancellation request for this booking has already been submitted. Our team will review your request shortly.")
        return redirect('my_bookings')

    cancellation_request = BookingCancellationRequest.objects.create(booking=booking)
    messages.success(request, "We have received your cancellation request. Our team will contact you once it is approved or rejected.", extra_tags="my_bookings")
    send_cancellation_request_notification_to_admin(booking, cancellation_request)
    return redirect('my_bookings')


#######################################
# Views responsible for booking changes
#######################################

@login_required
def edit_booking(request, booking_id):
    """
    Allows user to change bookings with status "Pending".
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Block changes if the booking is ongoing or in the past.
    if booking.start_date <= date.today():
        messages.error(request, "You can't change dates for an ongoing or past booking. Please visit the contact page for assistance.", extra_tags="my_bookings")
        return redirect('my_bookings')

    if booking.status != 'Pending':
        messages.error(request, "Self service is only available for pending bookings, please contact customer service.", extra_tags="my_bookings")
        return redirect('my_bookings')

    if request.method == "POST":
        new_start = request.POST.get("start_date")
        new_end = request.POST.get("end_date")

        try:
            new_start_dt = datetime.strptime(new_start, "%Y-%m-%d").date()
            new_end_dt = datetime.strptime(new_end, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.", extra_tags="my_bookings")
            return redirect('edit_booking', booking_id=booking_id)
        
        # Prevent past dates
        if new_start_dt < date.today():
            messages.error(request, "Invalid input. The start date can't be in the past.", extra_tags="my_bookings")
            return redirect('edit_booking', booking_id=booking_id)
        if new_end_dt < date.today():
            messages.error(request, "Invalid input. The end date can't be in the past.", extra_tags="my_bookings")
            return redirect('edit_booking', booking_id=booking_id)

        if new_end_dt <= new_start_dt:
            messages.error(request, "Invalid input. End date must be after start date.", extra_tags="my_bookings")
            return redirect('edit_booking', booking_id=booking_id)

        overlapping = Booking.objects.filter(
            campervan=booking.campervan,
            start_date__lt=new_end_dt,
            end_date__gt=new_start_dt
        ).exclude(id=booking.id).exclude(status='Cancelled')
        if overlapping.exists():
            messages.error(request, "This campervan is not available for the requested dates.", extra_tags="my_bookings")
            return redirect('edit_booking', booking_id=booking_id)

        day_count = (new_end_dt - new_start_dt).days
        booking.start_date = new_start_dt
        booking.end_date = new_end_dt
        booking.total_price = day_count * booking.campervan.price_per_day
        booking.save()

        send_booking_changed_email(booking)
        messages.success(request, "We successfully changed your booking!", extra_tags="my_bookings")
        return redirect('my_bookings')

    return render(request, 'booking/edit_booking.html', {
        'booking': booking,
    })


@login_required
def request_date_change(request, booking_id):
    """
    User can suggest a date change for a confirmed booking.
    Prevents requests if the booking is ongoing or in the past.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Block date change requests if booking has started or is in the past.
    if booking.start_date <= date.today():
        messages.error(request, "You can't request a date change for an ongoing or past booking. Please visit our contact page for assistance.", extra_tags="my_bookings")
        return redirect('my_bookings')

    if booking.status != 'Confirmed':
        messages.error(request, "Date change requests are only available for confirmed bookings - use self service for pending bookings instead.", extra_tags="my_bookings")
        return redirect('my_bookings')

    if request.method == "POST":
        new_start = request.POST.get("start_date")
        new_end = request.POST.get("end_date")

        try:
            new_start_dt = datetime.strptime(new_start, "%Y-%m-%d").date()
            new_end_dt = datetime.strptime(new_end, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.", extra_tags="my_bookings")
            return redirect('request_date_change', booking_id=booking_id)

        if new_end_dt <= new_start_dt:
            messages.error(request, "End date must be after start date.", extra_tags="my_bookings")
            return redirect('request_date_change', booking_id=booking_id)

        # Additional check: prevent setting new dates that are in the past.
        if new_start_dt < date.today():
            messages.error(request, "New start date cannot be in the past.", extra_tags="my_bookings")
            return redirect('request_date_change', booking_id=booking_id)

        bcr = BookingChangeRequest.objects.create(
            booking=booking,
            requested_start_date=new_start_dt,
            requested_end_date=new_end_dt
        )

        messages.success(request, "Your request has been submitted to our team for approval", extra_tags="my_bookings")
        send_date_change_request_received_email(booking, bcr)
        send_date_change_request_notification_to_admin(booking, bcr)
        return redirect('my_bookings')

    return render(request, 'booking/request_date_change.html', {'booking': booking})


########################################
# Views responsible for Admin / Staff functions
########################################

@staff_member_required
def view_change_requests(request):
    pending_requests = BookingChangeRequest.objects.filter(status='Pending')
    for req in pending_requests:
        day_count = (req.requested_end_date - req.requested_start_date).days
        req.new_total_price = day_count * req.booking.campervan.price_per_day
    return render(request, 'booking/change_requests.html', {
        'change_requests': pending_requests
    })


@staff_member_required
def approve_change_request(request, request_id):
    bcr = get_object_or_404(BookingChangeRequest, id=request_id, status='Pending')
    booking = bcr.booking

    overlapping = Booking.objects.filter(
        campervan=booking.campervan,
        start_date__lt=bcr.requested_end_date,
        end_date__gt=bcr.requested_start_date
    ).exclude(id=booking.id)
    if overlapping.exists():
        messages.error(request, "We're sorry. The requested dates are unavailable.")
        return redirect('view_change_requests')

    day_count = (bcr.requested_end_date - bcr.requested_start_date).days
    booking.start_date = bcr.requested_end_date - timedelta(days=day_count)  # or simply use bcr.requested_start_date
    booking.end_date = bcr.requested_end_date
    booking.total_price = day_count * booking.campervan.price_per_day
    booking.save()

    bcr.status = 'Approved'
    bcr.save()

    send_change_approval_email(booking, bcr)
    messages.success(request, f"Booking change request #{bcr.id} approved!")
    return redirect('view_change_requests')


@staff_member_required
def reject_change_request(request, request_id):
    bcr = get_object_or_404(BookingChangeRequest, id=request_id, status='Pending')
    bcr.status = 'Rejected'
    bcr.save()

    send_change_rejection_email(bcr.booking, bcr)
    messages.info(request, f"Booking change request #{bcr.id} has been rejected.")
    return redirect('view_change_requests')


#####################
# Email confirmations
#####################

def send_reservation_confirmation_email(booking):
    """
    Sends reservation confirmation email on successful reservation (before payment).
    """
    subject = 'Reservation Received'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"We have received your reservation for {booking.campervan.name} from {booking.start_date} to {booking.end_date}.\n"
        f"Please complete your payment within the next 3 days to confirm your booking by clicking on the 'Pay Now' button in your 'My Bookings' section.\n\n"
        f"Thank you for choosing us!\n\n"
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_booking_confirmation_email(booking):
    """
    Sends final confirmation email after payment is received.
    """
    subject = 'Booking Confirmed'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"We have received your payment and your booking for {booking.campervan.name} is now confirmed.\n"
        f"Start Date: {booking.start_date}\n"
        f"End Date: {booking.end_date}\n"
        f"Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for booking with us!\n\n"
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_cancellation_email(booking):
    """
    Sends confirmation email on cancelled bookings.
    """
    subject = 'Booking Cancellation'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} from {booking.start_date} to {booking.end_date} for ${booking.total_price:.2f} has been cancelled.\n"
        f"Thank you for your visit, we hope to see you soon again.\n\n"
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_booking_changed_email(booking):
    """
    Email confirmation after user changed booking via self service.
    """
    subject = 'Your booking has been successfully updated'
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your booking for {booking.campervan.name} has been updated.\n"
        f"New Start Date: {booking.start_date}\n"
        f"New End Date: {booking.end_date}\n"
        f"New Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for your visit, we hope to see you soon again.\n\n"
        f"Best regards,\n\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_date_change_request_received_email(booking, bcr):
    """
    Inform user that date change request needs admin approval.
    """
    subject = "Date change request received"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"We have received your date-change request for Booking #{booking.id}.\n"
        f"Requested Start: {bcr.requested_start_date}\n"
        f"Requested End: {bcr.requested_end_date}\n\n"
        f"Our team will review your request and notify you once it's approved or rejected."
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_date_change_request_notification_to_admin(booking, bcr):
    """
    Notification for admin about pending date change request.
    """
    admin_email = getattr(settings, 'DEFAULT_ADMIN_EMAIL', None)
    if not admin_email:
        return
    subject = f"New date change request is awaiting approval (Booking #{booking.id})"
    message = (
        f"Hello Admin, \n\n"
        f"User {booking.user.username} is requesting a date change for Booking #{booking.id}.\n"
        f"Requested Start: {bcr.requested_start_date}\n"
        f"Requested End: {bcr.requested_end_date}\n\n"
        f"Please review this request in the admin panel."
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [admin_email], fail_silently=False)


def send_change_approval_email(booking, bcr):
    """
    Sends email when a date change request is approved.
    """
    subject = "Your Date Change Request Was Approved"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your date change request for Booking #{booking.id} has been approved.\n"
        f"Here are your updated booking details:\n"
        f"Campervan: {booking.campervan.name}\n"
        f"New Start Date: {booking.start_date.strftime('%Y-%m-%d')}\n"
        f"New End Date: {booking.end_date.strftime('%Y-%m-%d')}\n"
        f"New Total Price: ${booking.total_price:.2f}\n\n"
        f"Thank you for booking with us!\n"
        f"Best regards,\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_change_rejection_email(booking, bcr):
    """
    Sends email when a date change request is rejected.
    """
    subject = "Your Date Change Request Was Rejected"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your date change request for Booking #{booking.id} has been rejected.\n"
        f"Your booking remains as follows:\n"
        f"Campervan: {booking.campervan.name}\n"
        f"Start Date: {booking.start_date.strftime('%Y-%m-%d')}\n"
        f"End Date: {booking.end_date.strftime('%Y-%m-%d')}\n"
        f"Total Price: ${booking.total_price:.2f}\n\n"
        f"In case you need further assistance, please contact our service team.\n"
        f"Best regards,\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_cancellation_approval_email(booking, cancellation_request):
    """
    Email confirmation for the user if cancellation request has been approved by admin.
    """
    subject = "Your cancellation request has been approved"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your cancellation request for Booking #{booking.id} has been approved.\n"
        f"Your booking is now cancelled.\n\n"
        f"Thank you for your visit. We hope to see you soon again.\n\n"
        f"Best regards,\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_cancellation_rejection_email(booking, cancellation_request):
    """
    Email confirmation for the user if cancellation request has been rejected by admin.
    """
    subject = "Your cancellation request has been rejected"
    message = (
        f"Dear {booking.user.username},\n\n"
        f"Your cancellation request for Booking #{booking.id} has been rejected.\n"
        f"Your booking remains confirmed.\n\n"
        f"In case you need further assistance, please contact our service team.\n\n"
        f"Best regards,\n"
        f"Your Wildventures Team"
    )
    send_mail(subject, message, 'no-reply@wildventures.com', [booking.user.email], fail_silently=False)


def send_cancellation_request_notification_to_admin(booking, cancellation_request):
    """
    Notify Admin about pending cancellation request.
    """
    admin_email = getattr(settings, 'DEFAULT_ADMIN_EMAIL', None)
    if admin_email:
        subject = f"Cancellation Request for Booking #{booking.id}"
        message = (
            f"User {booking.user.username} is requesting cancellation for Booking #{booking.id}.\n"
            "Please review this request in the admin dashboard."
        )
        send_mail(subject, message, 'no-reply@wildventures.com', [admin_email], fail_silently=False)