from django.db import models
from accounts.models import Funeraria, User
from inventario.models import Product
from vehiculos.models import Vehicle
from velatorios.models import SalaVelatorio
from storages.backends.s3boto3 import S3Boto3Storage
from django.utils import timezone

# Configuración para almacenar archivos en S3 (o local si lo prefieres)
class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

def custom_filename_fallecido(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"fallecido/documentos/{instance.rut}/{timestamp}_{nombre}.{extension}"

class Cliente(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    parentezco_con_fallecido = models.CharField(max_length=100)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.rut}"

class Fallecido(models.Model):
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    rut = models.CharField(max_length=12, unique=True)
    estado_civil = models.CharField(max_length=50)
    domicilio = models.CharField(max_length=255)
    nivel_estudios = models.CharField(max_length=100, blank=True, null=True)
    profesion = models.CharField(max_length=100, blank=True, null=True)
    lugar_fallecimiento = models.CharField(max_length=255)
    prevision = models.CharField(max_length=50)  # AFP/INP
    afp = models.CharField(max_length=100, blank=True, null=True)
    inp = models.CharField(max_length=100, blank=True, null=True)

    # Campos de documentos opcionales
    copia_cedula_identidad = models.FileField(storage=MediaStorage(), upload_to=custom_filename_fallecido, null=True, blank=True)
    certificado_defuncion = models.FileField(storage=MediaStorage(), upload_to=custom_filename_fallecido, null=True, blank=True)
    certificado_autorizacion_sepultacion = models.FileField(storage=MediaStorage(), upload_to=custom_filename_fallecido, null=True, blank=True)
    otros_documentos = models.FileField(storage=MediaStorage(), upload_to=custom_filename_fallecido, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.rut}"

class Contrato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fallecido = models.ForeignKey(Fallecido, on_delete=models.CASCADE)
    inventario = models.ForeignKey(Product, on_delete=models.CASCADE)  # Urna seleccionada
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)
    vehiculos = models.ManyToManyField(Vehicle)  # Puede haber uno o más vehículos
    trabajadores = models.ManyToManyField(User)  # Trabajadores vinculados al servicio
    sala_velatorio = models.ForeignKey(SalaVelatorio, on_delete=models.CASCADE, related_name="contratos")
    fecha_inicio_velatorio = models.DateTimeField()  # Inicio de la ocupación de la sala
    fecha_fin_velatorio = models.DateTimeField()  # Fin de la ocupación de la sala
    comuna_origen = models.CharField(max_length=100)
    comuna_destino = models.CharField(max_length=100, blank=True, null=True)
    cementerio_destino = models.CharField(max_length=255)
    es_traslado = models.BooleanField(default=False)  # True si la comuna de origen es distinta de la de destino
    valor_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    capilla = models.CharField(max_length=255)
    tipo_pago = models.CharField(max_length=100)
    condiciones_pago = models.TextField()
    estado_pago = models.CharField(max_length=50, choices=[
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('no_pagado', 'No Pagado')
    ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contrato {self.id} - Cliente: {self.cliente} - Fallecido: {self.fallecido}"