from rest_framework.routers import DefaultRouter
from .views import DocumentoImportanteViewSet

router = DefaultRouter()
router.register(r'documentos', DocumentoImportanteViewSet, basename='documentoimportante')

urlpatterns = router.urls
