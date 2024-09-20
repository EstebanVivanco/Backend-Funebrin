from rest_framework import serializers
from .models import Cliente, Fallecido, Contrato
from velatorios.models import SalaVelatorio
from inventario.models import Product
from vehiculos.models import Vehicle
from accounts.models import User

class ClienteSerializer(serializers.ModelSerializer):
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ['funeraria']

class FallecidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fallecido
        fields = '__all__'
        extra_kwargs = {
            'copia_cedula_identidad': {'required': False, 'allow_null': True},
            'certificado_defuncion': {'required': False, 'allow_null': True},
            'certificado_autorizacion_sepultacion': {'required': False, 'allow_null': True},
            'otros_documentos': {'required': False, 'allow_null': True}
        }


class ContratoSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())  # Se espera un ID
    fallecido = serializers.PrimaryKeyRelatedField(queryset=Fallecido.objects.all())  # Se espera un ID
    inventario = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    vehiculos = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), many=True)
    sala_velatorio = serializers.PrimaryKeyRelatedField(queryset=SalaVelatorio.objects.all())
    trabajadores = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'


    def create(self, validated_data):
        # Obtener los datos de cliente y fallecido del validated_data
        cliente_data = validated_data.pop('cliente')
        fallecido_data = validated_data.pop('fallecido')
        vehiculos_data = validated_data.pop('vehiculos')
        trabajadores_data = validated_data.pop('trabajadores')

        # Obtener el ID de la funeraria desde el usuario autenticado
        funeraria_id = self.context['request'].user.funeraria_id_id

        # Comprobar si cliente_data es un objeto o diccionario y actuar en consecuencia
        if isinstance(cliente_data, dict):
            # Crear o buscar el cliente y asignar funeraria_id
            cliente, _ = Cliente.objects.get_or_create(
                rut=cliente_data.get('rut'),
                defaults={
                    'nombres': cliente_data.get('nombres'),
                    'apellidos': cliente_data.get('apellidos'),
                    'telefono': cliente_data.get('telefono'),
                    'direccion': cliente_data.get('direccion'),
                    'parentezco_con_fallecido': cliente_data.get('parentezco_con_fallecido'),
                    'funeraria_id': funeraria_id
                }
            )
        else:
            cliente = cliente_data

        # Comprobar si fallecido_data es un objeto o diccionario y actuar en consecuencia
        if isinstance(fallecido_data, dict):
            fallecido, _ = Fallecido.objects.get_or_create(
                rut=fallecido_data.get('rut'),
                defaults=fallecido_data
            )
        else:
            fallecido = fallecido_data

        # Eliminar el campo funeraria de validated_data para evitar duplicados
        validated_data['funeraria_id'] = funeraria_id

        # Crear el contrato con el cliente y fallecido registrados
        contrato = Contrato.objects.create(
            cliente=cliente,
            fallecido=fallecido,
            **validated_data  # Ya no pasamos funeraria_id explícitamente
        )

        # Asignar vehículos y trabajadores
        contrato.vehiculos.set(vehiculos_data)
        contrato.trabajadores.set(trabajadores_data)

        return contrato
