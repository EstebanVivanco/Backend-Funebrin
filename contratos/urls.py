from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, ClienteViewSet, FallecidoViewSet, CotizacionViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)
router.register(r'cliente/contrato', ClienteViewSet)
router.register(r'fallecido/contrato', FallecidoViewSet)
router.register(r'cotizaciones', CotizacionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
