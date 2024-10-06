from rest_framework import serializers
from .models import Cliente, Fallecido, Contrato, Cotizacion
from velatorios.models import SalaVelatorio
from inventario.models import Product
from vehiculos.models import Vehicle
from accounts.models import User, Servicio

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

class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class SalaVelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaVelatorio
        fields = '__all__'

class TrabajadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    fallecido = FallecidoSerializer()
    inventario = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    vehiculos = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), many=True)
    sala_velatorio = serializers.PrimaryKeyRelatedField(queryset=SalaVelatorio.objects.all())
    trabajadores = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cliente'] = ClienteSerializer(instance.cliente).data
        data['inventario'] = InventarioSerializer(instance.inventario).data
        data['sala_velatorio'] = SalaVelatorioSerializer(instance.sala_velatorio).data
        data['vehiculos'] = VehiculoSerializer(instance.vehiculos.all(), many=True).data
        data['trabajadores'] = TrabajadorSerializer(instance.trabajadores.all(), many=True).data
        return data

    def create(self, validated_data):
        fallecido_data = validated_data.pop('fallecido')
        vehiculos_data = validated_data.pop('vehiculos')
        trabajadores_data = validated_data.pop('trabajadores')
        cliente = validated_data.pop('cliente')
        inventario = validated_data.pop('inventario')
        sala_velatorio = validated_data.pop('sala_velatorio')

        funeraria_id = self.context['request'].user.funeraria_id_id

        # Obtain files from request
        request = self.context.get('request')
        files = request.FILES

        # Create or update Fallecido, including files
        fallecido_serializer = FallecidoSerializer(data=fallecido_data)
        fallecido_serializer.is_valid(raise_exception=True)
        fallecido = fallecido_serializer.save(
            copia_cedula_identidad=files.get('copia_cedula_identidad'),
            certificado_defuncion=files.get('certificado_defuncion'),
            certificado_autorizacion_sepultacion=files.get('certificado_autorizacion_sepultacion'),
            otros_documentos=files.get('otros_documentos'),
        )

        validated_data['funeraria_id'] = funeraria_id

        # Check es_traslado
        comuna_origen = validated_data.get('comuna_origen')
        comuna_destino = validated_data.get('comuna_destino')
        validated_data['es_traslado'] = comuna_origen != comuna_destino

        # Create Contrato
        contrato = Contrato.objects.create(
            cliente=cliente,
            fallecido=fallecido,
            inventario=inventario,
            sala_velatorio=sala_velatorio,
            **validated_data
        )

        # Assign many-to-many fields
        contrato.vehiculos.set(vehiculos_data)
        contrato.trabajadores.set(trabajadores_data)

        return contrato


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'url_imagen', 'descripcion']  # Incluir los campos deseados



class CotizacionSerializer(serializers.ModelSerializer):
    servicios = ServicioSerializer(many=True)  # Incluir información detallada de los servicios

    class Meta:
        model = Cotizacion
        fields = '__all__'