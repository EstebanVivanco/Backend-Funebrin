from django.urls import path, include
from rest_framework import routers
from accounts import views
from .views import LoginView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'funerarias', views.FunerariaViewSet, basename='funerarias')
router.register(r'trabajadores', views.TrabajadorViewSet, basename='trabajadores')


urlpatterns = [
    path(r'cuentas/', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
