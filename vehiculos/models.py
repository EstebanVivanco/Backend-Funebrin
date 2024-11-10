from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage
from accounts.models import Funeraria

class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

# Función personalizada para imágenes de vehículos
def custom_filename_vehicle_image(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"vehicles/{instance.vehicle.id}/{timestamp}_{nombre}.{extension}"

# Función personalizada para documentos de vehículos
def custom_filename_vehicle_document(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"vehicles/{instance.vehicle.id}/documents/{timestamp}_{nombre}.{extension}"

class Vehicle(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True, null=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=100)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey('VehicleType', on_delete=models.CASCADE)
    visible = models.BooleanField(default=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE, related_name='vehiculos', null=True, blank=True)

    def __str__(self):
        return self.brand

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=MediaStorage(), upload_to=custom_filename_vehicle_image)

    def __str__(self):
        return f"Image for {self.vehicle.brand} {self.vehicle.model}"

class VehicleDocument(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document = models.FileField(storage=MediaStorage(), upload_to=custom_filename_vehicle_document)

    def __str__(self):
        return f"Document {self.title} for {self.vehicle.brand} {self.vehicle.model}"

class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name
