# urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from vehiculos import views

router = routers.DefaultRouter()
router.register(r'vehiculos', views.VehicleViewSet)
router.register(r'tipo-vehiculo', views.TypeVehicleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
