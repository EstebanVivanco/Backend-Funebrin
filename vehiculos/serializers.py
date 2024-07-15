from rest_framework import serializers
from .models import Vehicle, VehicleType

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class TypeVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'