from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import Funeraria, User  # Importar el modelo Funeraria y User

class SalaVelatorio(models.Model):
    nombre = models.CharField(max_length=255)
    capacidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE, related_name='salas_velatorio')
    encargado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='salas_encargado',
        limit_choices_to={'is_worker': True}  # Restringir a trabajadores
    )

    def __str__(self):
        return f"{self.nombre} - Capacidad: {self.capacidad}"

    def esta_disponible(self, fecha_inicio, fecha_fin):
        solapamientos = self.reservas.filter(
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        )
        return not solapamientos.exists()
class ReservaSala(models.Model):
    sala = models.ForeignKey(SalaVelatorio, on_delete=models.CASCADE, related_name='reservas')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    contrato = models.OneToOneField('contratos.Contrato', on_delete=models.CASCADE, related_name='reserva', null=True, blank=True)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE, related_name='reservas')

    def __str__(self):
        return f"Reserva de {self.sala.nombre} del {self.fecha_inicio} al {self.fecha_fin}"

    def clean(self):
        # Validar que fecha_fin es posterior a fecha_inicio
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # Verificar si hay reservas que se solapan
        solapamientos = ReservaSala.objects.filter(
            sala=self.sala,
            fecha_inicio__lt=self.fecha_fin,
            fecha_fin__gt=self.fecha_inicio
        ).exclude(id=self.id)

        if solapamientos.exists():
            raise ValidationError("La sala ya está reservada en este periodo.")

    def save(self, *args, **kwargs):
        # Asignar la funeraria automáticamente desde la sala
        self.funeraria = self.sala.funeraria
        self.full_clean()  # Llama al método clean() antes de guardar
        super().save(*args, **kwargs)