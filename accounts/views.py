from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import viewsets, serializers
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .serializers import UserSerializer, FunerariaSerializer, TrabajadorSerializer
from django.db import IntegrityError
from .models import User, Funeraria, Trabajador
from utils.swagger_utils import CustomTags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            # Agrega la información del usuario que deseas retornar
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "rut": user.rut,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "is_worker": user.is_worker,
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

@CustomTags.accounts
class FunerariaViewSet(viewsets.ModelViewSet):
    queryset = Funeraria.objects.all()
    serializer_class = FunerariaSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@CustomTags.trabajadores
class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.all()
    serializer_class = TrabajadorSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Obtén la funeraria del usuario autenticado
        user = self.request.user
        if user.is_anonymous:
            raise serializers.ValidationError("El usuario debe estar autenticado.")

        funeraria = None
        if user.is_admin:
            # El usuario es un administrador, obtener funeraria como admin
            funeraria = Funeraria.objects.filter(admin=user).first()
        elif user.is_worker:
            # El usuario es un trabajador, obtener funeraria desde el campo de trabajador
            funeraria = user.funeraria

        if not funeraria:
            raise serializers.ValidationError("Funeraria no encontrada para el usuario autenticado.")

        # Actualiza el contexto con la funeraria
        context = super().get_serializer_context()
        context.update({"funeraria": funeraria})
        return context

    @action(detail=False, methods=['get'], url_path='por-funeraria')
    def list_trabajadores_por_funeraria(self, request):
        # Obtener funeraria del usuario autenticado
        user = request.user
        funeraria = None
        if user.is_admin:
            funeraria = Funeraria.objects.filter(admin=user).first()
        elif user.is_worker:
            funeraria = user.funeraria

        if not funeraria:
            return Response({"error": "Funeraria no encontrada para el usuario autenticado."}, status=status.HTTP_404_NOT_FOUND)

        # Filtra los trabajadores por la funeraria
        trabajadores = Trabajador.objects.filter(funeraria=funeraria)
        serializer = self.get_serializer(trabajadores, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Aquí no necesitas pasar explícitamente funeraria ya que viene en el contexto
        serializer.save()
