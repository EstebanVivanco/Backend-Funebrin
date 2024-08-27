from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.auth.models import BaseUserManager

class MediaStorage(S3Boto3Storage):
    bucket_name = 'funebrinbucket'
    location = 'media/'

def custom_filename_funerarias(instance, filename: str):
    nombre = filename.split(".")
    extension = nombre.pop()
    nombre = nombre[0][:20]
    timestamp = timezone.now().strftime("%Y-%m-%dT%H-%M-%S")
    return f"funerarias/logos/{timestamp}_{nombre}.{extension}"

class Funeraria(models.Model):
    rut = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=14, default='Sin número', null=True, blank=True)
    email = models.EmailField()
    logo = models.ImageField(storage=MediaStorage(), upload_to=custom_filename_funerarias, null=True, blank=True)
    admin = models.OneToOneField('User', on_delete=models.CASCADE, related_name='funeraria_admin')

    def __str__(self):
        return self.name
    
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El campo email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    rut = models.CharField(max_length=16, unique=True)
    phone = models.CharField(max_length=14, default='Sin número', null=True, blank=True)
    username = models.CharField(max_length=150, unique=True, default='default_username')
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_worker = models.BooleanField(default=False)
    funeraria_id = models.ForeignKey('Funeraria', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    # Campos específicos para trabajadores
    contacto_telefono = models.CharField(max_length=14, null=True, blank=True)
    domicilio = models.CharField(max_length=255, null=True, blank=True)
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prevision = models.CharField(max_length=100, null=True, blank=True)
    sistema_salud = models.CharField(max_length=30, null=True, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    funcion = models.CharField(max_length=100, null=True, blank=True)

    groups = None
    user_permissions = None

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'rut']

    def __str__(self):
        return self.email
