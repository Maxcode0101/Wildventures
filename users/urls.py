from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('booking-history/', views.BookingHistoryView.as_view(), name='booking_history'),
]