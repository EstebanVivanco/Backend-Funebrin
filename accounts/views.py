from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, serializers, status
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializer, FunerariaSerializer, ServicioSerializer, LiquidacionSueldoSerializer
from django.db import IntegrityError
from .models import User, Funeraria, Servicio, LiquidacionSueldo
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from rest_framework.parsers import MultiPartParser, FormParser
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from decimal import Decimal
from datetime import date
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            funeraria_data = None
            if user.funeraria_id:
                funeraria_data = FunerariaSerializer(user.funeraria_id).data

            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "funcion": user.funcion,
                "rut": user.rut,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "is_worker": user.is_worker,
                "funeraria": funeraria_data
            }

            return Response({"token": token.key, "user": user_data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({"message": "Has cerrado sesión correctamente."})
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_admin:
                return User.objects.filter(funeraria_id=user.funeraria_id)
            else:
                return User.objects.filter(id=user.id)
        return User.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            funeraria = user.funeraria_id
            if funeraria:
                serializer.save(funeraria_id=funeraria)
            else:
                raise serializers.ValidationError("El administrador no tiene una funeraria asociada.")
        else:
            raise serializers.ValidationError("Solo los administradores pueden registrar trabajadores.")

    @action(detail=False, methods=['get'], url_path='por-funeraria')
    def list_trabajadores_por_funeraria(self, request):
        user = request.user
        funeraria = user.funeraria_id

        if not funeraria:
            return Response({"error": "Funeraria no encontrada para el usuario autenticado."}, status=status.HTTP_404_NOT_FOUND)

        trabajadores = User.objects.filter(funeraria_id=funeraria, is_worker=True)
        serializer = self.get_serializer(trabajadores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='total-sueldos-funeraria')
    def total_sueldos_funeraria(self, request):
        user = request.user
        funeraria = None

        if user.is_authenticated:
            if user.is_admin:
                funeraria = Funeraria.objects.filter(admin=user).first()
            elif user.is_worker:
                funeraria = user.funeraria_id

        if not funeraria:
            return Response({"error": "Funeraria no encontrada para el usuario autenticado."}, status=status.HTTP_404_NOT_FOUND)

        total_sueldos = User.objects.filter(funeraria_id=funeraria, is_worker=True).aggregate(total_sueldos=Sum('sueldo'))

        return Response({
            "total_sueldos": total_sueldos['total_sueldos'] or 0
        }, status=status.HTTP_200_OK)

class FunerariaViewSet(viewsets.ModelViewSet):
    queryset = Funeraria.objects.all()
    serializer_class = FunerariaSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='servicios')
    def obtener_servicios(self, request, pk=None):
        try:
            funeraria = Funeraria.objects.get(id=pk)
        except Funeraria.DoesNotExist:
            return Response({'error': 'Funeraria no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        servicios = funeraria.servicios.all()
        serializer = ServicioSerializer(servicios, many=True)
        return Response(serializer.data)

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    parser_classes = [MultiPartParser, FormParser]

class FunerariaDataView(APIView):
    def get(self, request, funeraria_id):
        try:
            funeraria = Funeraria.objects.get(id=funeraria_id)
        except Funeraria.DoesNotExist:
            return Response({'error': 'Funeraria no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # Aquí puedes agregar lógica adicional si es necesario

        return Response({'funeraria': FunerariaSerializer(funeraria).data}, status=status.HTTP_200_OK)

class LiquidacionSueldoViewSet(viewsets.ModelViewSet):
    queryset = LiquidacionSueldo.objects.all()
    serializer_class = LiquidacionSueldoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            funeraria = user.funeraria_id
            return LiquidacionSueldo.objects.filter(trabajador__funeraria_id=funeraria)
        else:
            return LiquidacionSueldo.objects.filter(trabajador=user)


    @action(detail=False, methods=['post'], url_path='generar-liquidaciones')
    def generar_liquidaciones(self, request):
        user = self.request.user
        if not user.is_admin:
            return Response({'detail': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        funeraria = user.funeraria_id
        if not funeraria:
            return Response({'detail': 'Funeraria no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        trabajadores = User.objects.filter(funeraria_id=funeraria, is_worker=True)
        liquidaciones_actualizadas = []
        today = date.today()
        fecha_liquidacion = date(today.year, today.month, 1)  # Primer día del mes actual

        for trabajador in trabajadores:
            sueldo_bruto = trabajador.sueldo or Decimal('0.00')

            # Convertir los porcentajes a Decimal para operaciones consistentes
            descuento_afp = sueldo_bruto * Decimal('0.10')  # 10% de AFP
            descuento_salud = sueldo_bruto * Decimal('0.07')  # 7% de salud
            descuentos = descuento_afp + descuento_salud
            sueldo_liquido = sueldo_bruto - descuentos

            # Verificar si ya existe la liquidación
            liquidacion, created = LiquidacionSueldo.objects.update_or_create(
                trabajador=trabajador,
                fecha=fecha_liquidacion,
                defaults={
                    'sueldo_bruto': sueldo_bruto,
                    'descuentos': descuentos,
                    'sueldo_liquido': sueldo_liquido,
                }
            )
            liquidaciones_actualizadas.append(liquidacion)

        serializer = self.get_serializer(liquidaciones_actualizadas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    @action(detail=True, methods=['get'], url_path='generar-pdf')
    def generar_pdf(self, request, pk=None):
        try:
            liquidacion = self.get_object()
        except LiquidacionSueldo.DoesNotExist:
            return HttpResponse('Liquidación no encontrada', status=404)

        trabajador = liquidacion.trabajador
        funeraria = trabajador.funeraria_id

        # Formatear la fecha actual en formato DD/MM/AAAA
        fecha_formateada = liquidacion.fecha.strftime('%d/%m/%Y')

        # Formatear los montos a moneda CLP con puntos en los miles
        sueldo_bruto = f"${liquidacion.sueldo_bruto:,.0f}".replace(',', '.')
        descuentos = f"${liquidacion.descuentos:,.0f}".replace(',', '.')
        sueldo_liquido = f"${liquidacion.sueldo_liquido:,.0f}".replace(',', '.')

        context = {
            'liquidacion': liquidacion,
            'trabajador': trabajador,
            'funeraria': funeraria,
            'fecha_formateada': fecha_formateada,
            'sueldo_bruto': sueldo_bruto,
            'descuentos': descuentos,
            'sueldo_liquido': sueldo_liquido,
        }

        html_string = render_to_string('liquidacion.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="liquidacion_{liquidacion.id}.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)
        return response


    @action(detail=False, methods=['get'], url_path='total-sueldos-mes')
    def total_sueldos_mes(self, request):
        user = self.request.user
        if not user.is_admin:
            return Response({'detail': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        funeraria = user.funeraria_id
        if not funeraria:
            return Response({'detail': 'Funeraria no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        today = date.today()
        fecha_liquidacion = date(today.year, today.month, 1)

        total_sueldos = LiquidacionSueldo.objects.filter(
            trabajador__funeraria_id=funeraria,
            fecha=fecha_liquidacion
        ).aggregate(total=Sum('sueldo_liquido'))['total'] or 0

        return Response({'total_sueldos_mes': total_sueldos}, status=status.HTTP_200_OK)
