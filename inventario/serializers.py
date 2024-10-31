from rest_framework import serializers
from .models import Product,  Proveedor, ProductImage, ProductMovement


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        exclude = ['funeraria']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source='image.url', read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_primary', 'alt_text', 'date_uploaded']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    images_to_remove = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    inventory_type_display = serializers.CharField(
        source='get_inventory_type_display', read_only=True
    )

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['funeraria']


class ProductMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductMovement
        fields = '__all__'

