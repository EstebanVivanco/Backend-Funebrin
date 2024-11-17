# velatorios/urls.py

from rest_framework.routers import DefaultRouter
from .views import SalaVelatorioViewSet, ReservaSalaViewSet,CondolenciaViewSet, salas_disponibles,salas_ocupadas_hoy, salas_ocupadas_futuro
from django.urls import path


router = DefaultRouter()
router.register(r'salas-velatorio', SalaVelatorioViewSet, basename='sala-velatorio')
router.register(r'reservas-salas', ReservaSalaViewSet, basename='reserva-sala')
router.register(r'condolencias', CondolenciaViewSet, basename='condolencias')

urlpatterns = router.urls

urlpatterns += [
    path('salas-velatorio/disponibles/', salas_disponibles, name='salas-disponibles'),
    path('salas-ocupadas/hoy/', salas_ocupadas_hoy, name='salas-ocupadas-hoy'),
    path('salas-ocupadas/futuro/', salas_ocupadas_futuro, name='salas-ocupadas-futuro'),
]
