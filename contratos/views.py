from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, Cliente, Fallecido
from .serializers import ContratoSerializer, ClienteSerializer, FallecidoSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

class FallecidoViewSet(viewsets.ModelViewSet):
    queryset = Fallecido.objects.all()
    serializer_class = FallecidoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Para manejar la carga de archivos

    @action(detail=True, methods=['patch'], url_path='subir-documentos')
    def subir_documentos(self, request, pk=None):
        fallecido = self.get_object()
        serializer = FallecidoSerializer(fallecido, data=request.data, partial=True)  # Permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    # Puedes agregar acciones personalizadas aquí si lo necesitas
    # Por ejemplo, buscar un cliente por su RUT o por otros campos
    @action(detail=False, methods=['get'], url_path='buscar-por-rut')
    def buscar_por_rut(self, request):
        rut = request.query_params.get('rut')
        if rut:
            try:
                cliente = Cliente.objects.get(rut=rut)
                serializer = self.get_serializer(cliente)
                return Response(serializer.data)
            except Cliente.DoesNotExist:
                return Response({"detail": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "RUT es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        funeraria_id = self.request.user.funeraria_id_id
        serializer.save(funeraria_id=funeraria_id)

    @action(detail=False, methods=['post'], url_path='buscar-o-crear-cliente')
    def buscar_o_crear_cliente(self, request):
        rut = request.data.get('rut')
        if not rut:
            return Response({"detail": "RUT es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la instancia de Funeraria en lugar de pasar el ID directamente
        funeraria = self.request.user.funeraria_id

        cliente_data = {
            "rut": rut,
            "nombres": request.data.get("nombres"),
            "apellidos": request.data.get("apellidos"),
            "telefono": request.data.get("telefono"),
            "direccion": request.data.get("direccion"),
            "parentezco_con_fallecido": request.data.get("parentezco_con_fallecido"),
            "funeraria": funeraria  # Aquí asignamos la instancia de Funeraria
        }

        cliente, created = Cliente.objects.get_or_create(rut=rut, defaults=cliente_data)
        serializer = ClienteSerializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='buscar-o-crear-fallecido')
    def buscar_o_crear_fallecido(self, request):
        rut = request.data.get('rut')
        if not rut:
            return Response({"detail": "RUT es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        fallecido_data = {
            "rut": rut,
            "nombres": request.data.get("nombres"),
            "apellidos": request.data.get("apellidos"),
            "estado_civil": request.data.get("estado_civil"),
            "domicilio": request.data.get("domicilio"),
            "lugar_fallecimiento": request.data.get("lugar_fallecimiento"),
            "prevision": request.data.get("prevision"),
        }

        fallecido, created = Fallecido.objects.get_or_create(rut=rut, defaults=fallecido_data)
        serializer = FallecidoSerializer(fallecido)
        return Response(serializer.data, status=status.HTTP_200_OK)