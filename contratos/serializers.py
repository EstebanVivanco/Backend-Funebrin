from rest_framework import serializers
from .models import Cliente, Fallecido, Contrato, Cotizacion, Funeraria, Exhumacion
from velatorios.models import SalaVelatorio
from inventario.models import Product
from vehiculos.models import Vehicle
from accounts.models import User, Servicio
from django.utils import timezone
import json
from django.apps import apps

class FunerariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funeraria
        fields = '__all__'  
class ClienteSerializer(serializers.ModelSerializer):
    funeraria = serializers.PrimaryKeyRelatedField(queryset=Funeraria.objects.all(), required=False)

    class Meta:
        model = Cliente
        fields = '__all__'

    def create(self, validated_data):
        if 'funeraria' not in validated_data or validated_data['funeraria'] is None:
            validated_data['funeraria'] = self.context['request'].user.funeraria_id
        return super().create(validated_data)



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
    sala_velatorio = serializers.PrimaryKeyRelatedField(
        queryset=SalaVelatorio.objects.all(),
        allow_null=True,
        required=False
    )
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    fallecido = FallecidoSerializer()
    inventario = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    vehiculos = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), many=True)
    trabajadores = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    funeraria = serializers.PrimaryKeyRelatedField(queryset=Funeraria.objects.all())

    class Meta:
        model = Contrato
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['cliente'] = ClienteSerializer(instance.cliente).data
        data['inventario'] = InventarioSerializer(instance.inventario).data
        data['sala_velatorio'] = SalaVelatorioSerializer(instance.sala_velatorio).data if instance.sala_velatorio else None
        data['vehiculos'] = VehiculoSerializer(instance.vehiculos.all(), many=True).data
        data['trabajadores'] = TrabajadorSerializer(instance.trabajadores.all(), many=True).data
        data['funeraria'] = FunerariaSerializer(instance.funeraria).data
        return data


    def create(self, validated_data):
        fallecido_data = validated_data.pop('fallecido')
        vehiculos_data = validated_data.pop('vehiculos')
        trabajadores_data = validated_data.pop('trabajadores')
        cliente = validated_data.pop('cliente')
        inventario = validated_data.pop('inventario')
        sala_velatorio = validated_data.pop('sala_velatorio')
        funeraria = validated_data.pop('funeraria')  # Obtén funeraria desde validated_data

        # Obtener archivos de la solicitud
        request = self.context.get('request')
        files = request.FILES

        # Crear o actualizar Fallecido, incluyendo archivos
        fallecido_serializer = FallecidoSerializer(data=fallecido_data)
        fallecido_serializer.is_valid(raise_exception=True)
        fallecido = fallecido_serializer.save(
            copia_cedula_identidad=files.get('copia_cedula_identidad'),
            certificado_defuncion=files.get('certificado_defuncion'),
            certificado_autorizacion_sepultacion=files.get('certificado_autorizacion_sepultacion'),
            otros_documentos=files.get('otros_documentos'),
        )

        # Verificar es_traslado
        comuna_origen = validated_data.get('comuna_origen')
        comuna_destino = validated_data.get('comuna_destino')
        validated_data['es_traslado'] = comuna_origen != comuna_destino

        # Crear Contrato
        contrato = Contrato.objects.create(
            cliente=cliente,
            fallecido=fallecido,
            inventario=inventario,
            sala_velatorio=sala_velatorio,
            funeraria=funeraria,  # Utiliza la funeraria proporcionada
            **validated_data
        )

        # Asignar campos many-to-many
        contrato.vehiculos.set(vehiculos_data)
        contrato.trabajadores.set(trabajadores_data)

        return contrato
    
    def validate(self, data):
        sala_velatorio = data.get('sala_velatorio')
        fecha_inicio = data.get('fecha_inicio_velatorio')
        fecha_fin = data.get('fecha_fin_velatorio')

        if sala_velatorio:
            if not fecha_inicio or not fecha_fin:
                raise serializers.ValidationError("Debe proporcionar las fechas de inicio y fin del velatorio.")

            # Verificar que la sala está disponible
            if not sala_velatorio.esta_disponible(fecha_inicio, fecha_fin):
                raise serializers.ValidationError("La sala velatorio seleccionada no está disponible en las fechas indicadas.")

        return data

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class CotizacionDetailSerializer(serializers.ModelSerializer):
    servicios = ServicioSerializer(many=True, read_only=True)

    class Meta:
        model = Cotizacion
        fields = '__all__'
        
class CotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cotizacion
        fields = '__all__'

class ExhumacionSerializer(serializers.ModelSerializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), required=False)
    fallecido = serializers.PrimaryKeyRelatedField(queryset=Fallecido.objects.all(), required=False)
    funeraria = serializers.PrimaryKeyRelatedField(queryset=Funeraria.objects.all(), required=False)

    class Meta:
        model = Exhumacion
        fields = '__all__'

    def to_internal_value(self, data):
        # Make a mutable copy of data
        data = data.copy()

        # Handle 'cliente'
        cliente_data = data.get('cliente')
        if cliente_data:
            if isinstance(cliente_data, str):
                # Try to parse as JSON
                try:
                    cliente_data_parsed = json.loads(cliente_data)
                    if isinstance(cliente_data_parsed, dict):
                        # Create Cliente instance
                        cliente_serializer = ClienteSerializer(data=cliente_data_parsed, context=self.context)
                        cliente_serializer.is_valid(raise_exception=True)
                        cliente = cliente_serializer.save()
                        data['cliente'] = cliente.id
                    elif cliente_data.isdigit():
                        data['cliente'] = int(cliente_data)
                    else:
                        raise serializers.ValidationError({'cliente': 'Invalid cliente data'})
                except json.JSONDecodeError:
                    # Not JSON, could be an ID
                    if cliente_data.isdigit():
                        data['cliente'] = int(cliente_data)
                    else:
                        raise serializers.ValidationError({'cliente': 'Invalid cliente data'})
            elif isinstance(cliente_data, dict):
                cliente_serializer = ClienteSerializer(data=cliente_data, context=self.context)
                cliente_serializer.is_valid(raise_exception=True)
                cliente = cliente_serializer.save()
                data['cliente'] = cliente.id
            else:
                raise serializers.ValidationError({'cliente': 'Invalid cliente data'})

        # Handle 'fallecido'
        fallecido_data = data.get('fallecido')
        if fallecido_data:
            if isinstance(fallecido_data, str):
                # Try to parse as JSON
                try:
                    fallecido_data_parsed = json.loads(fallecido_data)
                    if isinstance(fallecido_data_parsed, dict):
                        # Create Fallecido instance
                        fallecido_serializer = FallecidoSerializer(data=fallecido_data_parsed, context=self.context)
                        fallecido_serializer.is_valid(raise_exception=True)
                        fallecido = fallecido_serializer.save()
                        data['fallecido'] = fallecido.id
                    elif fallecido_data.isdigit():
                        data['fallecido'] = int(fallecido_data)
                    else:
                        raise serializers.ValidationError({'fallecido': 'Invalid fallecido data'})
                except json.JSONDecodeError:
                    # Not JSON, could be an ID
                    if fallecido_data.isdigit():
                        data['fallecido'] = int(fallecido_data)
                    else:
                        raise serializers.ValidationError({'fallecido': 'Invalid fallecido data'})
            elif isinstance(fallecido_data, dict):
                fallecido_serializer = FallecidoSerializer(data=fallecido_data, context=self.context)
                fallecido_serializer.is_valid(raise_exception=True)
                fallecido = fallecido_serializer.save()
                data['fallecido'] = fallecido.id
            else:
                raise serializers.ValidationError({'fallecido': 'Invalid fallecido data'})

        return super().to_internal_value(data)

    def create(self, validated_data):
        # Assign 'funeraria' from the authenticated user if not provided
        if 'funeraria' not in validated_data or validated_data['funeraria'] is None:
            validated_data['funeraria'] = self.context['request'].user.funeraria_id
        return super().create(validated_data)
class ClienteDetailSerializer(serializers.ModelSerializer):
    class Meta:
            model = Cliente
            fields = ['id', 'nombres', 'apellidos', 'rut', 'telefono', 'direccion', 'parentezco_con_fallecido']

class FallecidoDetailSerializer(serializers.ModelSerializer):
    class Meta:
            model = Fallecido
            fields = ['id', 'nombres', 'apellidos', 'rut', 'estado_civil', 'domicilio', 'lugar_fallecimiento', 'prevision']

class ExhumacionDetailSerializer(serializers.ModelSerializer):
    cliente = ClienteDetailSerializer(read_only=True)
    fallecido = FallecidoDetailSerializer(read_only=True)
    funeraria = FunerariaSerializer(read_only=True)

    class Meta:
        model = Exhumacion
        fields = '__all__'