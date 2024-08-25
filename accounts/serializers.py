from rest_framework import serializers
from .models import Funeraria, User, Trabajador
from django.contrib.auth import get_user_model

User = get_user_model()

from rest_framework import serializers
from .models import Funeraria, User, Trabajador

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

from rest_framework import serializers
from .models import Funeraria, User

from rest_framework import serializers
from .models import Funeraria, User

class FunerariaSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True)
    admin_rut = serializers.CharField(write_only=True)
    admin_phone = serializers.CharField(write_only=True)

    class Meta:
        model = Funeraria
        fields = ['rut', 'name', 'location', 'phone', 'email', 'logo', 'admin_email', 'admin_password', 'admin_rut', 'admin_phone']

    def create(self, validated_data):
        admin_email = validated_data.pop('admin_email')
        admin_password = validated_data.pop('admin_password')
        admin_rut = validated_data.pop('admin_rut')
        admin_phone = validated_data.pop('admin_phone')

        # Verificar si ya existe un usuario con el mismo rut
        if User.objects.filter(rut=admin_rut).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT.")

        # Crear el usuario admin sin asignar una funeraria todavía
        admin_user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            rut=admin_rut,
            phone=admin_phone,
            is_staff=True,
            is_admin=True,
        )

        # Crear la funeraria con el admin asociado
        funeraria = Funeraria.objects.create(admin=admin_user, **validated_data)

        # Asociar el admin con la funeraria
        admin_user.funeraria = funeraria
        admin_user.save()

        return funeraria

class TrabajadorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)  # Este campo es de solo lectura ahora

    class Meta:
        model = Trabajador
        fields = ['user', 'phone', 'rut', 'contacto_telefono', 'email_contacto', 'domicilio', 'sueldo', 'prevision', 'sistema_salud', 'fecha_contratacion', 'funcion', 'funeraria']
        extra_kwargs = {
            'funeraria': {'read_only': True},  # Asegúrate de que el campo funeraria sea solo lectura
        }

    def create(self, validated_data):
        # Extrae los datos relacionados con el usuario
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        email = user_data.pop('email')

        # Obtén la funeraria del contexto
        funeraria = self.context.get('funeraria', None)
        if not funeraria:
            raise serializers.ValidationError("Funeraria no encontrada en el contexto.")

        # Crea el usuario y asigna la funeraria
        user = User.objects.create_worker(email=email, password=password, **user_data)
        user.funeraria = funeraria
        user.save()

        # Crea el trabajador relacionado con la funeraria
        trabajador = Trabajador.objects.create(user=user, funeraria=funeraria, **validated_data)
        
        return trabajador