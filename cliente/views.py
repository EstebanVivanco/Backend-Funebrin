from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ClienteSerializer, TipoClienteSerializer
from .models import Cliente, TipoCliente
from utils.swagger_utils import CustomTags


# Create your views here.
@CustomTags.cliente
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

@CustomTags.tipoCliente
class TipoClienteViewSet(viewsets.ModelViewSet):
    queryset = TipoCliente.objects.all()
    serializer_class = TipoClienteSerializer