from rest_framework import serializers
from .models import Product, ProductType

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
class TypeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'