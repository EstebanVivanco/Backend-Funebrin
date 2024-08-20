from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import viewsets, serializers
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from .serializers import UserSerializer, FunerariaSerializer, TrabajadorSerializer
from .models import User, Funeraria, Trabajador
from utils.swagger_utils import CustomTags
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

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

@CustomTags.accounts
class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.all()
    serializer_class = TrabajadorSerializer

    def get_serializer_context(self):
        user = self.request.user
        funeraria = Funeraria.objects.get(admin=user)
        context = super().get_serializer_context()
        context.update({"funeraria": funeraria})
        return context