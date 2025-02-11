from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('users/', include('users.urls')),
    path('booking/', include('booking.urls')),
    path('campervans/', views.campervan_list, name='campervan_list'),
    path('check-availability/', views.check_availability, name='check_availability'),
]
