from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:campervan_id>/', views.book_campervan, name='book_campervan'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
