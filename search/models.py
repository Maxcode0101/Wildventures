from django.db import models
from cloudinary.models import CloudinaryField


# Stores details about campervans.
class Campervan(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
    available_from = models.DateField()
    available_to = models.DateField()
    description = models.TextField()
    image = CloudinaryField('image')

    def __str__(self):
        return self.name

