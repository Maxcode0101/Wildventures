from django.contrib import admin
from .models import Booking, BookingChangeRequest, BookingCancellationRequest
from .views import (
    send_change_approval_email,
    send_change_rejection_email,
    send_cancellation_approval_email,
    send_cancellation_rejection_email,
)


# Register Booking model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "campervan",
        "start_date",
        "end_date",
        "total_price",
        "status",
    )
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("user__username", "campervan__name")


@admin.register(BookingChangeRequest)
class BookingChangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "requested_start_date",
        "requested_end_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("booking__id", "booking__user__username")

    def save_model(self, request, obj, form, change):
        # Check if it is a change request (change == True)
        if change:
            # Fetch the initial version from the DB
            prev_obj = BookingChangeRequest.objects.get(pk=obj.pk)
            if prev_obj.status != obj.status:
                # Admin changed booking status: Call email function
                if obj.status == "Approved":
                    booking = obj.booking
                    # Update booking with data from admin console
                    booking.start_date = obj.requested_start_date
                    booking.end_date = obj.requested_end_date
                    # Recalc. price
                    day_count = (booking.end_date - booking.start_date).days
                    booking.total_price = (
                        day_count * booking.campervan.price_per_day
                    )
                    booking.save()
                    send_change_approval_email(obj.booking, obj)
                elif obj.status == "Rejected":
                    send_change_rejection_email(obj.booking, obj)
            super().save_model(request, obj, form, change)


@admin.register(BookingCancellationRequest)
class BookingCancellationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("booking__id", "booking__user__username")

    def save_model(self, request, obj, form, change):
        booking = obj.booking
        # Update the booking if the cancellation request is approved.
        if obj.status == "Approved":
            booking.status = "Cancelled"
            booking.save()
            send_cancellation_approval_email(booking, obj)
        elif obj.status == "Rejected":
            send_cancellation_rejection_email(booking, obj)
        super().save_model(request, obj, form, change)
