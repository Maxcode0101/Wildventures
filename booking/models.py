from django.db import models

# Handles details about bookings
from django.db import models
from django.contrib.auth.models import User
from core.models import Campervan

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    campervan = models.ForeignKey(Campervan, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Booking by {self.user} for {self.campervan} from {self.start_date} to {self.end_date}"
