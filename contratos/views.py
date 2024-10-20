from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from django.utils.translation import gettext as _
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Cotizacion
from .serializers import CotizacionSerializer, CotizacionDetailSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa  
from datetime import datetime
import locale

class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        servicios_data = self.request.data.pop('servicios', [])
        cotizacion = serializer.save()
        cotizacion.servicios.set(servicios_data)
        cotizacion.save()

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        cotizacion = self.get_object()
        nuevo_estado = request.data.get('estado')
        if nuevo_estado in ['pendiente', 'aprobado', 'rechazado']:
            cotizacion.estado = nuevo_estado
            cotizacion.save()
            return Response({"estado": cotizacion.estado}, status=status.HTTP_200_OK)
        return Response({"detail": "Estado inválido"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='por-funeraria')
    def listar_por_funeraria(self, request):
        # Obtener funeraria del usuario autenticado
        funeraria_id = request.user.funeraria_id_id

        # Filtrar cotizaciones por funeraria_id
        cotizaciones = Cotizacion.objects.filter(funeraria_id=funeraria_id)
        serializer = CotizacionDetailSerializer(cotizaciones, many=True, context={'request': request})
        return Response(serializer.data)

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
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_context(self):
        return {'request': self.request}


    def perform_create(self, serializer):
        serializer.save()

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

    @action(detail=True, methods=['get'], url_path='generar-pdf')
    def generar_pdf_contrato(self, request, pk=None):
        # Configurar el locale para español (es_ES). Asegúrate de que esté disponible en tu sistema.
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para sistemas Unix/Linux

        # Obtener el contrato por su ID
        try:
            contrato = Contrato.objects.get(id=pk)
        except Contrato.DoesNotExist:
            return HttpResponse('Contrato no encontrado', status=404)

        # Obtener la fecha actual y formatearla en español
        fecha_actual = datetime.now().strftime('%d de %B de %Y')

        # Formatear las fechas del contrato
        fecha_inicio_velatorio = contrato.fecha_inicio_velatorio.strftime('%d de %B de %Y')
        fecha_fin_velatorio = contrato.fecha_fin_velatorio.strftime('%d de %B de %Y')

        # Formatear el valor del servicio con separadores de miles para CLP
        valor_servicio = "${:,.0f}".format(contrato.valor_servicio).replace(",", ".")

        # Preparar los datos para el template
        context = {
            'contrato': contrato,
            'cliente': contrato.cliente,
            'fallecido': contrato.fallecido,
            'inventario': contrato.inventario,
            'vehiculos': contrato.vehiculos.all(),
            'funeraria': contrato.funeraria,
            'sala_velatorio': contrato.sala_velatorio,
            'trabajadores': contrato.trabajadores.all(),
            'fecha_actual': fecha_actual,  # Fecha actual en español
            'fecha_inicio_velatorio': fecha_inicio_velatorio,  # Fecha de inicio del velatorio en español
            'fecha_fin_velatorio': fecha_fin_velatorio,  # Fecha de fin del velatorio en español
            'valor_servicio': valor_servicio  # Valor formateado con CLP
        }

        # Renderizar el template a HTML
        html_string = render_to_string('contrato.html', context)

        # Crear una respuesta de tipo PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="contrato_{pk}.pdf"'

        # Convertir HTML a PDF usando xhtml2pdf
        pisa_status = pisa.CreatePDF(html_string, dest=response)

        # Verificar si hubo errores
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)
        return response
