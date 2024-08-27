from rest_framework import serializers
from .models import Funeraria, User

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

        if User.objects.filter(rut=admin_rut).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT.")

        admin_user = User.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            rut=admin_rut,
            phone=admin_phone,
            is_staff=True,
            is_admin=True,
        )

        funeraria = Funeraria.objects.create(admin=admin_user, **validated_data)

        admin_user.funeraria_id = funeraria
        admin_user.save()

        return funeraria
