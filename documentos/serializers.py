from rest_framework import serializers
from .models import DocumentoImportante

class DocumentoImportanteSerializer(serializers.ModelSerializer):
    archivo_url = serializers.CharField(source='archivo.url', read_only=True)
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DocumentoImportante
        fields = '__all__'
        read_only_fields = ['fecha_subida', 'funeraria']