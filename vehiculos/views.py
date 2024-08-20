# views.py
from rest_framework import viewsets
from .serializers import VehicleSerializer, TypeVehicleSerializer
from .models import Vehicle, VehicleType
from utils.swagger_utils import CustomTags
from rest_framework.permissions import IsAuthenticated

@CustomTags.vehicles
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]  # Asegura que el usuario esté autenticado

    def perform_create(self, serializer):
        user = self.request.user
        funeraria = user.funeraria_admin  # Obtener la funeraria asociada al admin
        serializer.save(funeraria=funeraria)

@CustomTags.typeVehicle
class TypeVehicleViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = TypeVehicleSerializer
