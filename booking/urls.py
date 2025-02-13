from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:campervan_id>/', views.book_campervan, name='book_campervan'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('status/<int:booking_id>/', views.check_booking_status, name='check_booking_status'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking_details/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('request_date_change/<int:booking_id>/', views.request_date_change, name='request_date_change'),
    path('change_requests/', views.view_change_requests, name='view_change_requests'),  # Admin route
    path('change_requests/<int:request_id>/approve/', views.approve_change_request, name='approve_change_request'),
    path('change_requests/<int:request_id>/reject/', views.reject_change_request, name='reject_change_request'),
    path('request_cancellation/<int:booking_id>/', views.request_cancellation, name='request_cancellation'),
    path('create-checkout-session/<int:booking_id>/', create_checkout_session, name='create_checkout_session'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
]