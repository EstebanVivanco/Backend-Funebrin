from django.db import models
from accounts.models import Funeraria  # Importar Funeraria
from storages.backends.s3boto3 import S3Boto3Storage
from django.utils import timezone

class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

def custom_filename_document(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"documentos/{instance.funeraria.id}/{timestamp}_{nombre}.{extension}"

class DocumentoImportante(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    tipo_documento = models.CharField(max_length=100)  # Campo CharField para tipo de documento
    archivo = models.FileField(storage=MediaStorage(), upload_to=custom_filename_document)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
