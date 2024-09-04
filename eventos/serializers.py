from rest_framework import serializers
from .models import Event, EventAssignment

class EventAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAssignment
        fields = ['worker']

class EventSerializer(serializers.ModelSerializer):
    assignments = EventAssignmentSerializer(many=True, write_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'event_type', 'created_by', 'funeraria', 'assignments']
        read_only_fields = ['created_by', 'funeraria']

    def create(self, validated_data):
        assignments_data = validated_data.pop('assignments', [])
        event = Event.objects.create(**validated_data)

        # Check if the event is created successfully
        if event.id:
            print(f"Event created with ID: {event.id}")
        else:
            print("Event creation failed.")

        for assignment_data in assignments_data:
            # Check if each assignment data is being processed
            print(f"Creating assignment for worker: {assignment_data['worker']}")
            EventAssignment.objects.create(event=event, **assignment_data)

        return event

