from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, ClienteViewSet, FallecidoViewSet, CotizacionViewSet, ExhumacionViewSet, ExhumacionDetailViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)
router.register(r'cliente/contrato', ClienteViewSet, basename='cliente-contrato')
router.register(r'fallecido/contrato', FallecidoViewSet)
router.register(r'cotizaciones', CotizacionViewSet)
router.register(r'exhumaciones', ExhumacionViewSet)  # Agrega el nuevo ViewSet para exhumaciones
router.register(r'exhumaciones-detalle', ExhumacionDetailViewSet, basename='exhumaciones-detalle')


urlpatterns = [
    path('', include(router.urls)),
]
