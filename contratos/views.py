from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, Cliente, Fallecido
from .serializers import ContratoSerializer, ClienteSerializer, FallecidoSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.utils.timezone import now
import calendar
from django.utils.translation import gettext as _
from rest_framework.parsers import MultiPartParser, FormParser

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
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Incluir JSONParser

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        funeraria_id = self.request.user.funeraria_id_id
        serializer.save(funeraria_id=funeraria_id)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        funeraria_id = self.request.user.funeraria_id_id
        serializer.save(funeraria_id=funeraria_id)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        funeraria_id = self.request.user.funeraria_id_id
        serializer.save(funeraria_id=funeraria_id)
        
    # Nueva acción personalizada para listar contratos con es_traslado=True y filtrados por funeraria_id
    @action(detail=False, methods=['get'], url_path='traslados')
    def listar_traslados(self, request):
        # Obtener funeraria del usuario autenticado
        funeraria_id = self.request.user.funeraria_id_id
        
        # Filtrar contratos por funeraria_id y es_traslado=True
        contratos_traslado = Contrato.objects.filter(funeraria_id=funeraria_id, es_traslado=True)
        
        # Serializar los contratos filtrados
        serializer = self.get_serializer(contratos_traslado, many=True)
        return Response(serializer.data)
    
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
    
    
    
        # Ruta para obtener el total del valor de contratos por estado de pago en el mes actual basado en la funeraria
    @action(detail=False, methods=['get'], url_path='total-valor-mes-actual')
    def total_valor_mes_actual(self, request):
        funeraria_id = request.user.funeraria_id_id
        today = now().date()
        current_month = today.month
        current_year = today.year

        # Filtrar contratos por el mes y año actual y la funeraria del usuario
        contratos_pendientes = Contrato.objects.filter(
            fecha_creacion__month=current_month,
            fecha_creacion__year=current_year,
            funeraria_id=funeraria_id,
            estado_pago='pendiente'
        ).aggregate(total_pendiente=Sum('valor_servicio'))

        contratos_pagados = Contrato.objects.filter(
            fecha_creacion__month=current_month,
            fecha_creacion__year=current_year,
            funeraria_id=funeraria_id,
            estado_pago='pagado'
        ).aggregate(total_pagado=Sum('valor_servicio'))

        contratos_no_pagados = Contrato.objects.filter(
            fecha_creacion__month=current_month,
            fecha_creacion__year=current_year,
            funeraria_id=funeraria_id,
            estado_pago='no_pagado'
        ).aggregate(total_no_pagado=Sum('valor_servicio'))

        return Response({
            'total_pendiente': contratos_pendientes['total_pendiente'] or 0,
            'total_pagado': contratos_pagados['total_pagado'] or 0,
            'total_no_pagado': contratos_no_pagados['total_no_pagado'] or 0,
        }, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['get'], url_path='total-valor-por-mes-ano-actual')
    def total_valor_por_mes_ano_actual(self, request):
        funeraria_id = request.user.funeraria_id_id
        today = now().date()
        current_year = today.year

        # Lista de todos los meses del año actual
        meses_del_ano = [datetime(current_year, mes, 1) for mes in range(1, 13)]

        # Nombres de los meses en español
        meses_esp = [
            _('Enero'), _('Febrero'), _('Marzo'), _('Abril'), _('Mayo'), _('Junio'),
            _('Julio'), _('Agosto'), _('Septiembre'), _('Octubre'), _('Noviembre'), _('Diciembre')
        ]

        # Obtener los contratos agrupados por mes para cada estado de pago
        contratos_por_mes = Contrato.objects.filter(
            fecha_creacion__year=current_year,
            funeraria_id=funeraria_id,
        ).annotate(mes=TruncMonth('fecha_creacion')).values('mes', 'estado_pago').annotate(
            total_valor=Sum('valor_servicio')
        ).order_by('mes')

        # Crear un diccionario con los valores por mes y estado_pago
        totales_por_mes = {}
        for contrato in contratos_por_mes:
            mes = contrato['mes'].month  # Obtener el número de mes
            estado_pago = contrato['estado_pago']
            total_valor = contrato['total_valor']

            if mes not in totales_por_mes:
                totales_por_mes[mes] = {'total_pagado': 0, 'total_pendiente': 0, 'total_no_pagado': 0}

            if estado_pago == 'pagado':
                totales_por_mes[mes]['total_pagado'] += total_valor
            elif estado_pago == 'pendiente':
                totales_por_mes[mes]['total_pendiente'] += total_valor
            elif estado_pago == 'no_pagado':
                totales_por_mes[mes]['total_no_pagado'] += total_valor

        # Unificar los resultados garantizando que todos los meses estén presentes
        resultados = []
        for mes in range(1, 13):
            resultados.append({
                'mes': meses_esp[mes - 1],  # Nombre del mes en español
                'total_pagado': totales_por_mes.get(mes, {}).get('total_pagado', 0),
                'total_pendiente': totales_por_mes.get(mes, {}).get('total_pendiente', 0),
                'total_no_pagado': totales_por_mes.get(mes, {}).get('total_no_pagado', 0),
            })

        return Response(resultados, status=status.HTTP_200_OK)
