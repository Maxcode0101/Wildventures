from django.db import models
from cloudinary.models import CloudinaryField


# Stores details about campervans
class Campervan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    image = CloudinaryField("image")  # Image field for campervan photos
    location = models.CharField(max_length=100)
    availability_status = models.BooleanField(default=True)  # True = Available
    capacity = models.IntegerField()  # Max number of people
    brand = models.CharField(
        max_length=50, blank=True, null=True
    )  # Vehicle brand
    model = models.CharField(
        max_length=50, blank=True, null=True
    )  # Vehicle model

    def __str__(self):
        return self.name

    def is_available(self, start_date, end_date):
        """Check if campervan is available for the given date range."""
        overlapping_bookings = self.booking_set.filter(
            models.Q(start_date__lte=end_date)
            & models.Q(end_date__gte=start_date)
        )
        return not overlapping_bookings.exists()
