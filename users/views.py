from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from .forms import UserRegisterForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add user data to context
        context['user'] = self.request.user

        # Add placeholders for bookings (to be implemented later)
        context['past_bookings'] = []  # Replace with actual query for past bookings
        context['upcoming_bookings'] = []  # Replace with actual query for upcoming bookings

        return context

def custom_logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')