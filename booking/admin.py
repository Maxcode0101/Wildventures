from django.contrib import admin
from .models import Booking

# Register Booking model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'campervan', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'campervan__name')