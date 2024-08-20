# serializers.py
from rest_framework import serializers
from .models import Vehicle, VehicleType

from rest_framework import serializers
from .models import Vehicle, VehicleType, Funeraria

class VehicleSerializer(serializers.ModelSerializer):
    funeraria = serializers.PrimaryKeyRelatedField(queryset=Funeraria.objects.all(), required=False)

    class Meta:
        model = Vehicle
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class TypeVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'
