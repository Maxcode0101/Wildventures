from django.contrib import admin
from .models import Campervan

# Update the Admin Panel to include new fields
@admin.register(Campervan)
class CampervanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_day', 'location', 'availability_status', 'capacity')
    list_filter = ('availability_status', 'location')  # Filter by these fields
    search_fields = ('name', 'location')  # Search by name and location
