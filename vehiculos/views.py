from django.shortcuts import render
from rest_framework import viewsets
from .serializers import VehicleSerializer, TypeVehicleSerializer
from .models import Vehicle, VehicleType
from utils.swagger_utils import CustomTags


@CustomTags.vehicles
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

@CustomTags.typeVehicle
class TypeVehicleViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = TypeVehicleSerializer


