from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Event
from .serializers import EventSerializer, ReservaSalaSerializer, ExhumacionSerializer
from velatorios.models import ReservaSala
from contratos.models import Exhumacion
from django.utils import timezone
from datetime import datetime, time
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

class EventViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,  # Agregamos DestroyModelMixin
                   mixins.RetrieveModelMixin,  # Agregamos RetrieveModelMixin
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user.funeraria_id:
            return []

        funeraria = user.funeraria_id

        # Obtener eventos propios
        events = Event.objects.filter(funeraria=funeraria)
        # Obtener reservas de salas
        reservas = ReservaSala.objects.filter(funeraria=funeraria)
        # Obtener exhumaciones
        exhumaciones = Exhumacion.objects.filter(funeraria=funeraria)

        # Combinar todos los objetos en una lista
        combined = list(events) + list(reservas) + list(exhumaciones)

        # Función para asegurar que los datetime sean con zona horaria
        def get_aware_datetime(dt):
            if dt is None:
                return None
            if timezone.is_naive(dt):
                return timezone.make_aware(dt)
            else:
                return dt

        # Función para obtener la fecha de inicio según el tipo de objeto
        def get_start_time(obj):
            default_datetime = timezone.make_aware(datetime(1970, 1, 1))
            if isinstance(obj, Event):
                dt = obj.start_time or default_datetime
                return get_aware_datetime(dt)
            elif isinstance(obj, ReservaSala):
                dt = obj.fecha_inicio or default_datetime
                return get_aware_datetime(dt)
            elif isinstance(obj, Exhumacion):
                fecha = obj.fecha_exhumacion
                if fecha:
                    # Convertir fecha_exhumacion (DateField) a datetime
                    dt = datetime.combine(fecha, time.min)
                    return get_aware_datetime(dt)
                else:
                    return default_datetime
            else:
                return default_datetime  # Valor por defecto si no hay fecha

        # Ordenar la lista por fecha de inicio
        combined.sort(key=get_start_time)

        return combined

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []

        for obj in queryset:
            if isinstance(obj, Event):
                serializer = EventSerializer(obj)
            elif isinstance(obj, ReservaSala):
                serializer = ReservaSalaSerializer(obj)
            elif isinstance(obj, Exhumacion):
                serializer = ExhumacionSerializer(obj)
            data.append(serializer.data)

        return Response(data)

    def get_serializer_class(self):
        if self.action == 'create':
            return EventSerializer
        if self.action == 'destroy':
            return EventSerializer
        return None  # Se utiliza el serializador adecuado en la función `list`

    def perform_create(self, serializer):
        if not self.request.user.funeraria_id:
            raise ValidationError("El usuario no tiene una funeraria asociada.")
        
        funeraria = self.request.user.funeraria_id
        serializer.save(created_by=self.request.user, funeraria=funeraria)

    def get_object(self):
        # Sobrescribimos get_object para obtener la instancia específica de Event
        queryset = Event.objects.filter(funeraria=self.request.user.funeraria_id)
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        if not isinstance(event, Event):
            return Response({'detail': 'No se puede eliminar este tipo de evento.'}, status=status.HTTP_400_BAD_REQUEST)
        # Verificar si el usuario tiene permiso para eliminar el evento
        if request.user != event.created_by and not request.user.is_admin:
            return Response({'detail': 'No tienes permiso para eliminar este evento.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
