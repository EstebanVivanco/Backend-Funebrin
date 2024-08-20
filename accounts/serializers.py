from rest_framework import serializers
from .models import Funeraria, User, Trabajador
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class FunerariaSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True)

    class Meta:
        model = Funeraria
        fields = ['rut', 'name', 'location', 'phone', 'email', 'logo', 'admin_email', 'admin_password']

    def create(self, validated_data):
        admin_email = validated_data.pop('admin_email')
        admin_password = validated_data.pop('admin_password')

        # Crear el usuario admin
        admin_user = User.objects.create_user(
            email=admin_email,
            password=admin_password,
            is_staff=True,
            is_admin=True,
        )

        # Crear la funeraria con el admin asociado
        funeraria = Funeraria.objects.create(admin=admin_user, **validated_data)

        return funeraria

class TrabajadorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)  # Marcar como read_only

    class Meta:
        model = Trabajador
        fields = '__all__'

    def create(self, validated_data):
        # Extrae los datos relacionados con el usuario
        user_data = validated_data.pop('user')

        # Extrae el password y el email de user_data
        password = user_data.pop('password', None)
        email = user_data.pop('email')

        # Crea el usuario
        user = User.objects.create_user(email=email, password=password, **user_data)
        user.is_worker = True
        user.save()

        # Obtén la funeraria del contexto
        funeraria = self.context.get('funeraria', None)

        if not funeraria:
            raise serializers.ValidationError("Funeraria no encontrada en el contexto.")

        # Crea el trabajador relacionado con la funeraria
        trabajador = Trabajador.objects.create(user=user, funeraria=funeraria, **validated_data)
        
        return trabajador
