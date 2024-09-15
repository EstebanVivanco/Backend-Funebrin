from rest_framework import serializers
from .models import SalaVelatorio, ReservaSala

class SalaVelatorioSerializer(serializers.ModelSerializer):
    funeraria = serializers.PrimaryKeyRelatedField(read_only=True, source='funeraria_id')

    class Meta:
        model = SalaVelatorio
        fields = '__all__'
        read_only_fields = ['fecha_subida', 'funeraria']


class ReservaSalaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaSala
        fields = '__all__'

    def validate(self, data):
        sala = data['sala']
        fecha_inicio = data['fecha_inicio']
        fecha_fin = data['fecha_fin']

        if fecha_fin <= fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        if not sala.esta_disponible(fecha_inicio, fecha_fin):
            raise serializers.ValidationError("La sala ya está reservada en este periodo.")

        return data
