from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import viewsets, serializers
from django.views.decorators.csrf import csrf_exempt
from .serializers import UserSerializer, FunerariaSerializer, ServicioSerializer
from django.db import IntegrityError
from .models import User, Funeraria, Servicio
from utils.swagger_utils import CustomTags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from rest_framework.parsers import MultiPartParser, FormParser

from inventario.models import Product
from inventario.serializers import ProductSerializer

from vehiculos.models import Vehicle
from vehiculos.serializers import VehicleSerializer

from accounts.models import Funeraria

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)

            # Serializar los datos de la funeraria
            funeraria_data = None
            if user.funeraria_id:
                funeraria_data = FunerariaSerializer(user.funeraria_id).data

            # Datos del usuario
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "rut": user.rut,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "is_worker": user.is_worker,
                "funeraria": funeraria_data  # Incluir los datos de la funeraria
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

@CustomTags.accounts
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_admin:
                return User.objects.all()
            else:
                return User.objects.filter(id=user.id)
        return User.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        funeraria = None
        if user.is_authenticated:
            if user.is_admin:
                funeraria = Funeraria.objects.filter(admin=user).first()
            elif user.is_worker:
                funeraria = user.funeraria_id
        if funeraria:
            context.update({"funeraria": funeraria})
        return context

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated and user.is_admin:
            funeraria = Funeraria.objects.filter(admin=user).first()
            if funeraria:
                serializer.save(funeraria_id=funeraria)
            else:
                raise serializers.ValidationError("El administrador no tiene una funeraria asociada.")
        else:
            raise serializers.ValidationError("Solo los administradores pueden registrar trabajadores.")

    @action(detail=False, methods=['get'], url_path='por-funeraria')
    def list_trabajadores_por_funeraria(self, request):
        user = request.user
        funeraria = None

        if user.is_authenticated:
            if user.is_admin:
                funeraria = Funeraria.objects.filter(admin=user).first()
            elif user.is_worker:
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

@CustomTags.accounts
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
        
        # Obtener los servicios asociados a la funeraria
        servicios = funeraria.servicios.all()
        serializer = ServicioSerializer(servicios, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    parser_classes = [MultiPartParser, FormParser]

class FunerariaDataView(APIView):
    # Eliminar el uso de IsAuthenticated para permitir el acceso sin protección
    def get(self, request, funeraria_id):
        try:
            funeraria = Funeraria.objects.get(id=funeraria_id)
        except Funeraria.DoesNotExist:
            return Response({'error': 'Funeraria no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los vehículos e inventario asociados a la funeraria
        vehicles = Vehicle.objects.filter(funeraria=funeraria)
        products = Product.objects.filter(funeraria=funeraria)
        services = funeraria.servicios.all()

        vehicle_serializer = VehicleSerializer(vehicles, many=True)
        product_serializer = ProductSerializer(products, many=True)
        servicio_serializer = ServicioSerializer(services, many=True)
        
        data = {
            'funeraria': {
                'id': funeraria.id,
                'rut': funeraria.rut,
                'name': funeraria.name,
                'location': funeraria.location,
                'phone': funeraria.phone,
                'email': funeraria.email,
                # Agrega otros campos necesarios de la funeraria
                 'servicios': servicio_serializer.data,
            },
            'vehicles': vehicle_serializer.data,
            'inventory': product_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)