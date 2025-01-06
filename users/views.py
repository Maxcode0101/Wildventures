from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from .forms import UserRegisterForm
from bookings.models import Booking  # Replace with the actual model for user bookings if applicable

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# User Profile View (Authenticated Access Only)
@login_required
def profile(request):
    """View to display the user's profile."""
    return render(request, 'users/profile.html')

# User Dashboard View (Class-Based, Authenticated Access Only)
class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard page for authenticated users."""
    template_name = 'users/dashboard.html'

# Booking History View for Users (Authenticated Access Only)
class BookingHistoryView(LoginRequiredMixin, ListView):
    """View to display the user's booking history."""
    model = Booking  # Assuming there's a Booking model
    template_name = 'users/booking_history.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        """Fetch bookings specific to the logged-in user."""
        return self.model.objects.filter(user=self.request.user)