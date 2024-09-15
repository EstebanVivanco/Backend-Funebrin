from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DocumentoImportante
from .serializers import DocumentoImportanteSerializer
from utils.swagger_utils import CustomTags

@CustomTags.documentos
class DocumentoImportanteViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentoImportanteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Para manejar archivos

    def get_queryset(self):
        # Filtrar documentos por la funeraria del usuario autenticado
        return DocumentoImportante.objects.filter(funeraria=self.request.user.funeraria_id)

    def perform_create(self, serializer):
        # Asignar funeraria al crear el documento
        funeraria = self.request.user.funeraria_id
        serializer.save(funeraria=funeraria)
