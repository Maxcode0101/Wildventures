from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from booking.models import Booking 
from datetime import date

# User Profile View - Only for Logged-in Users
@login_required
def profile(request):
    """Show the user's profile"""
    return render(request, 'users/profile.html')

@login_required
def dashboard(request):
    """Show the user's dashboard with their bookings"""
    # Get all bookings for the current user
    user_bookings = Booking.objects.filter(user=request.user)

    # Split bookings into upcoming and past
    upcoming_bookings = user_bookings.filter(start_date__gte=date.today()).order_by("start_date")
    past_bookings = user_bookings.filter(end_date__lt=date.today()).order_by("-end_date")

    # Set up data for the template
    template = 'users/dashboard.html'
    context = {
    "upcoming_bookings": upcoming_bookings,
    "past_bookings": past_bookings,
    }

    return render(request, "users/dashboard.html", context)


@login_required
def my_bookings(request):
    """
    Show users bookings
    """
    user_bookings = Booking.objects.filter(user=request.user).order_by('-start_date')
    return render(request, 'users/my_bookings.html', {'bookings': user_bookings})
    