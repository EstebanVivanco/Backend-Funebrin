from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from cliente import views

router = routers.DefaultRouter()
router.register(r'cliente', views.ClienteViewSet)
router.register(r'tipo-cliente', views.TipoClienteViewSet)  

urlpatterns = [
    path('', include(router.urls)),
]
