from django.urls import path, include
from rest_framework import routers
from inventario import views

router = routers.DefaultRouter()
router.register(r'inventario', views.ProductViewSet, basename='inventario')
router.register(r'proveedores', views.ProveedorViewSet, basename='proveedores')
router.register(r'movimientos-producto', views.ProductMovementViewSet, basename='movimientos-producto')

urlpatterns = [
    path('', include(router.urls)),
]
