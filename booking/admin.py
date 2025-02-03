from django.contrib import admin
from .models import Booking, BookingChangeRequest

# Register Booking model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'campervan', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'campervan__name')
    

@admin.register(BookingChangeRequest)
class BookingChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'requested_start_date', 'requested_end_date', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__id', 'booking__user__username')