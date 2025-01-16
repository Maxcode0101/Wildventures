from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

# from bookings.models import Booking

# User Profile View (Authenticated Access Only)
@login_required
def profile(request):
    """View to display the user's profile."""
    return render(request, 'users/profile.html')

@login_required
def dashboard(request):
    # past_bookings = Booking.objects.filter(end_date__lt=now().date(), renter=request.user)
    # upcoming_bookings = Booking.objects.filter(start_date__gte=now().date(), renter=request.user)
    template = 'users/dashboard.html'
    context = {
        # "past_bookings": past_bookings,
        # "upcoming_bookings": upcoming_bookings,
    }

    return render(request, template, context)