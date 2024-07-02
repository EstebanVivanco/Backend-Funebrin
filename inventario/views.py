from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ProductSerializer, TypeProductSerializer
from .models import Product, ProductType
from utils.swagger_utils import CustomTags


# Create your views here.
@CustomTags.inventary
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@CustomTags.inventary
class TypeProductViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = TypeProductSerializer