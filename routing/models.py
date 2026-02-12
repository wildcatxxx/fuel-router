from django.contrib.gis.db import models

# Create your models here.
class TruckStop(models.Model):
    opis_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    rack_id = models.CharField(max_length=50)
    retail_price = models.DecimalField(max_digits=6, decimal_places=3)

    location = models.PointField(geography=True)

    class Meta:
        indexes = [
            models.Index(fields=["opis_id"]),
            models.Index(fields=["retail_price"]),
            models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.city}, {self.state})"