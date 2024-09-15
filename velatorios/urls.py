# velatorios/urls.py

from rest_framework.routers import DefaultRouter
from .views import SalaVelatorioViewSet, ReservaSalaViewSet, salas_disponibles
from django.urls import path

router = DefaultRouter()
router.register(r'salas-velatorio', SalaVelatorioViewSet, basename='sala-velatorio')
router.register(r'reservas-salas', ReservaSalaViewSet, basename='reserva-sala')

urlpatterns = router.urls

urlpatterns += [
    path('salas-velatorio/disponibles/', salas_disponibles, name='salas-disponibles'),
]
