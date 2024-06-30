from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from accounts import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet , 'users')

urlpatterns = [
    path('cuentas/', include(router.urls)),
]

