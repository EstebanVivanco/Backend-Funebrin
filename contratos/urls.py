from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, ClienteViewSet, FallecidoViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)
router.register(r'cliente/contrato', ClienteViewSet)  # Añadir ruta para cliente
router.register(r'fallecido/contrato', FallecidoViewSet)  # Añadir ruta para fallecido

urlpatterns = [
    path('', include(router.urls)),
]
