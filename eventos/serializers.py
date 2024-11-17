from rest_framework import serializers
from .models import Event, EventAssignment
from velatorios.models import ReservaSala
from contratos.models import Exhumacion

class EventAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAssignment
        fields = ['worker']

class EventSerializer(serializers.ModelSerializer):
    assignments = EventAssignmentSerializer(many=True, write_only=True)
    tipo_evento = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time',
            'event_type', 'created_by', 'funeraria', 'assignments',
            'tipo_evento'
        ]
        read_only_fields = ['created_by', 'funeraria']

    def get_tipo_evento(self, obj):
        return 'evento'

    def create(self, validated_data):
        assignments_data = validated_data.pop('assignments', [])
        event = Event.objects.create(**validated_data)

        for assignment_data in assignments_data:
            EventAssignment.objects.create(event=event, **assignment_data)

        return event

class ReservaSalaSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='sala.nombre')
    start_time = serializers.DateTimeField(source='fecha_inicio')
    end_time = serializers.DateTimeField(source='fecha_fin')
    tipo_evento = serializers.SerializerMethodField()

    class Meta:
        model = ReservaSala
        fields = ['id', 'title', 'start_time', 'end_time', 'tipo_evento']

    def get_tipo_evento(self, obj):
        return 'reserva_sala'

class ExhumacionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start_time = serializers.DateField(source='fecha_exhumacion')
    end_time = serializers.DateField(source='fecha_exhumacion')
    tipo_evento = serializers.SerializerMethodField()

    class Meta:
        model = Exhumacion
        fields = ['id', 'title', 'start_time', 'end_time', 'tipo_evento']

    def get_title(self, obj):
        return f"Exhumación de {obj.fallecido.nombres} {obj.fallecido.apellidos}"

    def get_tipo_evento(self, obj):
        return 'exhumacion'