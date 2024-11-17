# velatorios/views.py

from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import SalaVelatorio, ReservaSala, Condolencia
from .serializers import SalaVelatorioSerializer, ReservaSalaSerializer, CondolenciaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from contratos.serializers import ContratoSerializer
from django.db.models import Q
from accounts.models import Funeraria
from contratos.models import Fallecido, Contrato
class SalaVelatorioViewSet(viewsets.ModelViewSet):
    serializer_class = SalaVelatorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SalaVelatorio.objects.filter(funeraria_id=self.request.user.funeraria_id)

    def perform_create(self, serializer):
        # Asignar funeraria al crear el documento
        funeraria = self.request.user.funeraria_id
        serializer.save(funeraria=funeraria)

class ReservaSalaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSalaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReservaSala.objects.filter(funeraria=self.request.user.funeraria_id)

@api_view(['GET'])
def salas_disponibles(request):
    fecha_inicio_str = request.query_params.get('fecha_inicio')
    fecha_fin_str = request.query_params.get('fecha_fin')

    if not fecha_inicio_str or not fecha_fin_str:
        return Response({'detail': 'Debe proporcionar fecha_inicio y fecha_fin.'}, status=400)

    try:
        fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
        fecha_fin = datetime.fromisoformat(fecha_fin_str)
    except ValueError:
        return Response({'detail': 'Formato de fecha inválido. Use el formato ISO.'}, status=400)

    fecha_inicio = timezone.make_aware(fecha_inicio, timezone.get_current_timezone())
    fecha_fin = timezone.make_aware(fecha_fin, timezone.get_current_timezone())

    salas = SalaVelatorio.objects.filter(funeraria_id=request.user.funeraria_id)
    salas_disponibles = []

    for sala in salas:
        if sala.esta_disponible(fecha_inicio, fecha_fin):
            salas_disponibles.append(sala)

    serializer = SalaVelatorioSerializer(salas_disponibles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def salas_ocupadas_hoy(request):
    hoy = timezone.now().date()
    reservas_hoy = ReservaSala.objects.filter(
        Q(fecha_inicio__date__lte=hoy) & Q(fecha_fin__date__gte=hoy),
        funeraria=request.user.funeraria_id
    )

    data = []
    for reserva in reservas_hoy:
        contrato_serializer = ContratoSerializer(reserva.contrato)
        data.append({
            'sala': reserva.sala.nombre,
            'fecha_inicio': reserva.fecha_inicio,
            'fecha_fin': reserva.fecha_fin,
            'contrato': contrato_serializer.data
        })

    return Response(data)


@api_view(['GET'])
def salas_ocupadas_futuro(request):
    hoy = timezone.now().date()
    reservas_futuras = ReservaSala.objects.filter(
        fecha_inicio__date__gt=hoy,
        funeraria=request.user.funeraria_id
    )

    data = []
    for reserva in reservas_futuras:
        contrato_serializer = ContratoSerializer(reserva.contrato)
        data.append({
            'sala': reserva.sala.nombre,
            'fecha_inicio': reserva.fecha_inicio,
            'fecha_fin': reserva.fecha_fin,
            'contrato': contrato_serializer.data
        })

    return Response(data)

class CondolenciaViewSet(viewsets.ModelViewSet):
    serializer_class = CondolenciaSerializer
    permission_classes = [AllowAny]  # Permitir a cualquiera dejar una condolencia

    def get_queryset(self):
        fallecido_id = self.request.query_params.get('fallecido_id')
        if fallecido_id:
            return Condolencia.objects.filter(fallecido_id=fallecido_id)
        else:
            return Condolencia.objects.all()

    def perform_create(self, serializer):
        fallecido_id = self.request.data.get('fallecido')
        if not fallecido_id:
            raise serializers.ValidationError("El campo 'fallecido' es obligatorio.")

        try:
            fallecido = Fallecido.objects.get(id=fallecido_id)
        except Fallecido.DoesNotExist:
            raise serializers.ValidationError("El fallecido especificado no existe.")

        # Obtener el contrato asociado al fallecido
        contrato = Contrato.objects.filter(fallecido=fallecido).first()
        if not contrato:
            raise serializers.ValidationError("No se encontró un contrato asociado al fallecido.")

        # Obtener la funeraria y la reserva de sala desde el contrato
        funeraria = contrato.funeraria
        reserva_sala = contrato.reserva  # 'reserva' es el related_name definido en el modelo Contrato

        if not reserva_sala:
            raise serializers.ValidationError("No se encontró una reserva de sala asociada al contrato.")

        # Guardar la condolencia con los campos adicionales
        serializer.save(funeraria=funeraria, reserva_sala=reserva_sala)