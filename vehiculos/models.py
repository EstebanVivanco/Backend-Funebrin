# models.py
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage
from accounts.models import Funeraria  # Asegúrate de importar el modelo correctamente

class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

def custom_filename_vehicles(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"vehicles/{timestamp}_{nombre}.{extension}"

class Vehicle(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True, null=True)  # Asegúrate de que esta línea esté presente
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(storage=MediaStorage(), upload_to=custom_filename_vehicles)
    date_added = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)
    funeraria = models.ForeignKey('accounts.Funeraria', on_delete=models.CASCADE, related_name='vehiculos', null=True, blank=True)

    def __str__(self):
        return self.brand

class VehicleType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
