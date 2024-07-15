from django.db import models

# Create your models here.
class Vehicle (models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    RegistrationNumber = models.CharField(max_length=100, unique=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)

    def __str__(self):
        return self.brand
    
class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name