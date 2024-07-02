from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from inventario import views

router = routers.DefaultRouter()
router.register(r'inventario', views.ProductViewSet )

urlpatterns = [
    path('', include(router.urls)),
]

