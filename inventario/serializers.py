from rest_framework import serializers
from .models import Product, ProductType, Proveedor, ProductImage

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        exclude = ['funeraria']

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='image.url', read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # Incluir imágenes

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['funeraria']

class TypeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'
