from django.urls import path
from . import views

urlpatterns = [
    path('', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('campervans/', views.campervan_list, name='campervan_list'),
    path('check-availability/', views.check_availability, name='check_availability'),
]
