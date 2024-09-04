from django.urls import path, include
from rest_framework import routers
from inventario import views

router = routers.DefaultRouter()
router.register(r'inventario', views.ProductViewSet, basename='inventario')
router.register(r'tipo-producto', views.TypeProductViewSet, basename='tipo-producto')
router.register(r'proveedores', views.ProveedorViewSet, basename='proveedores')  # Ruta para el proveedor

urlpatterns = [
    path('', include(router.urls)),
]
