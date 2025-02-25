# Handles details about bookings
from django.db import models
from django.contrib.auth.models import User
from core.models import Campervan
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings"
    )
    campervan = models.ForeignKey(
        Campervan, on_delete=models.CASCADE, related_name="bookings"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user} for {self.campervan} from {self.start_date} to {self.end_date}" #noqa


# User requests changes related to a booking
class BookingChangeRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="change_requests"
    )
    requested_start_date = models.DateField()
    requested_end_date = models.DateField()
    status = models.CharField(
        max_length=8, choices=STATUS_CHOICES, default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f"Change Request for Booking {self.booking.id} ({self.status})"


# User requests cancelation of a booking
class BookingCancellationRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]
    booking = models.ForeignKey(
        "Booking",
        on_delete=models.CASCADE,
        related_name="cancellation_requests",
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation Request for Booking {self.booking.id} ({self.status})" #noqa

    # Ensures that status updates beeing saved
    def save(self, *args, **kwargs):
        if self.pk:
            previous = BookingCancellationRequest.objects.get(pk=self.pk)
            if previous.status != self.status:
                if self.status == "Approved":
                    self.booking.status = "Cancelled"
                    self.booking.save()
        super().save(*args, **kwargs)


@receiver(pre_save, sender=BookingCancellationRequest)
def update_booking_status_on_cancellation(sender, instance, **kwargs):
    """
    Check if status has changed from "Approved" to "Cancelled"
    """
    if instance.pk:
        # Load the initial status from DB
        previous = BookingCancellationRequest.objects.get(pk=instance.pk)
        if (
            previous.status != instance.status
            and instance.status == "Approved"
        ):
            instance.booking.status = "Cancelled"
            instance.booking.save()
