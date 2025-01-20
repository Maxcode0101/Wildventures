from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path('admin/', admin.site.urls),  # Admin URL
    path('users/', include('users.urls')),  # Include users app URLs
    path('', include('core.urls')),  # Include core app URLs
    path('booking/', include('booking.urls')), # Include booking app URLs
]
