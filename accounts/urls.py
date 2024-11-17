from django.urls import path, include
from rest_framework import routers
from accounts import views
from .views import LoginView, FunerariaDataView, LiquidacionSueldoViewSet

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'funerarias', views.FunerariaViewSet, basename='funerarias')
router.register(r'servicios', views.ServicioViewSet, basename='servicios')
router.register(r'liquidaciones', LiquidacionSueldoViewSet, basename='liquidaciones')

urlpatterns = [
    path('cuentas/', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('funerarias/<int:funeraria_id>/datos/', FunerariaDataView.as_view(), name='funeraria-datos'),
]
