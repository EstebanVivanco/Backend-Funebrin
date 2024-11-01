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

class InventoryType(models.TextChoices):
    INTERNO = 'IN', 'Interno'
    EXTERNO = 'EX', 'Externo'

class Product(models.Model):
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    material = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    color = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    capacity = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    wood_type = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    style = models.CharField(max_length=100, null=True, blank=True)  # Nuevo campo
    date_added = models.DateTimeField(auto_now_add=True)
    tipo_ventidible = models.CharField(max_length=100, null=True, blank=True)  # Cambiado el nombre del campo
    vendible = models.BooleanField(default=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)
    inventory_type = models.CharField(
        max_length=2,
        choices=InventoryType.choices,
        default=InventoryType.INTERNO
    )
    min_stock_level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
class ProductMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()  # Cantidad positiva o negativa para entradas/salidas
    description = models.CharField(max_length=255)
    movement_type = models.CharField(
        max_length=10,
        choices=[('Entrada', 'Entrada'), ('Salida', 'Salida')]
    )

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=MediaStorage(), upload_to=custom_filename_product)
    is_primary = models.BooleanField(default=False)  # Campo para marcar la imagen principal del producto
    alt_text = models.CharField(max_length=255, null=True, blank=True)  # Texto alternativo para accesibilidad
    date_uploaded = models.DateTimeField(auto_now_add=True)  # Fecha de carga de la imagen

    def __str__(self):
        return f"Image for {self.product.name}"
