from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut = models.CharField(max_length=13, unique=True)
    telefono = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True)
    direccion = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    tipo_cliente = models.ForeignKey('TipoCliente', on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre + ' ' + self.apellido


class TipoCliente(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
