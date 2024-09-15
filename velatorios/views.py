# velatorios/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SalaVelatorio, ReservaSala
from .serializers import SalaVelatorioSerializer, ReservaSalaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime


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
        return ReservaSala.objects.filter(sala__funeraria_id=self.request.user.funeraria_id)

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
