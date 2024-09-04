from django.db import models
from accounts.models import Funeraria  # Importar Funeraria
from storages.backends.s3boto3 import S3Boto3Storage
from django.utils import timezone

class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

def custom_filename_product(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"productos/{instance.product.id}/{timestamp}_{nombre}.{extension}"

class Proveedor(models.Model):
    name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)  # Relación con Funeraria

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    material = models.CharField(max_length=100, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    vendible = models.BooleanField(default=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)  # Campo de proveedor
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)  # Nuevo campo para relacionar el producto con la funeraria
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=MediaStorage(), upload_to=custom_filename_product)

    def __str__(self):
        return f"Image for {self.product.name}"
