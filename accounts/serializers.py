from rest_framework import serializers
from .models import Funeraria, User, Servicio

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        funeraria = validated_data.pop('funeraria_id', None)
        
        # Crea el usuario usando el manager personalizado
        user = User.objects.create_user(**validated_data)
        
        # Asigna la funeraria_id al usuario si está presente
        if funeraria:
            user.funeraria_id = funeraria  # Asigna la instancia de funeraria
            user.save()
        
        return user

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'url_imagen', 'descripcion']

class FunerariaSerializer(serializers.ModelSerializer):
    admin_email = serializers.EmailField(write_only=True)
    admin_password = serializers.CharField(write_only=True)
    admin_rut = serializers.CharField(write_only=True)
    admin_phone = serializers.CharField(write_only=True)
    servicios = serializers.PrimaryKeyRelatedField(many=True, queryset=Servicio.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Funeraria
        fields = ['rut', 'name', 'location', 'phone', 'email', 'logo','phonefijo','admin_email', 'admin_password', 'admin_rut', 'admin_phone', 'servicios']

    def create(self, validated_data):
        admin_email = validated_data.pop('admin_email')
        admin_password = validated_data.pop('admin_password')
        admin_rut = validated_data.pop('admin_rut')
        admin_phone = validated_data.pop('admin_phone')

        if User.objects.filter(rut=admin_rut).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT.")

        # Crear administrador
        admin_user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            rut=admin_rut,
            phone=admin_phone,
            is_staff=True,
            is_admin=True,
        )

        # Extraer servicios antes de crear la funeraria
        servicios_data = validated_data.pop('servicios', [])

        # Crear funeraria
        funeraria = Funeraria.objects.create(admin=admin_user, **validated_data)

        # Asignar servicios a la funeraria
        funeraria.servicios.set(servicios_data)

        # Asignar funeraria al administrador
        admin_user.funeraria_id = funeraria
        admin_user.save()

        return funeraria
