from django.db import models
from cloudinary.models import CloudinaryField

# Stores details about campervans
class Campervan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    image = CloudinaryField('image')  # Image field for campervan photos
    location = models.CharField(max_length=100)
    availability_status = models.BooleanField(default=True)  # True = Available
    capacity = models.IntegerField()  # Max number of people
    brand = models.CharField(max_length=50, blank=True, null=True) # Vehicle brand
    model = models.CharField(max_length=50, blank=True, null=True) # Vehicle model

    def __str__(self):
        return self.name
