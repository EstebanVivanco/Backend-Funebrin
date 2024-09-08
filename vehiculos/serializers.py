from rest_framework import serializers
from .models import Vehicle, VehicleType, VehicleImage, VehicleDocument, Funeraria

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'image']

class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ['id', 'title', 'document']

class VehicleSerializer(serializers.ModelSerializer):
    funeraria = serializers.PrimaryKeyRelatedField(queryset=Funeraria.objects.all(), required=False)
    images = VehicleImageSerializer(many=True, read_only=True)
    documents = VehicleDocumentSerializer(many=True, read_only=True)
    
    # Campos adicionales para eliminar imágenes y documentos
    images_to_remove = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )
    documents_to_remove = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Vehicle
        fields = '__all__'


class TypeVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'
