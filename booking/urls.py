from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:campervan_id>/', views.book_campervan, name='book_campervan'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('status/<int:booking_id>/', views.check_booking_status, name='check_booking_status'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('booking_details/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
