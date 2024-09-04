from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Event, EventAssignment
from accounts.models import User  # Correct import for User model
from .serializers import EventSerializer
from django.shortcuts import get_object_or_404

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the user has a funeraria associated
        if not self.request.user.funeraria_id:
            print("User does not have an associated funeraria.")
            return Response({"error": "User does not have an associated funeraria."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Automatically set the user creating the event and the associated funeraria
        funeraria = self.request.user.funeraria_id
        print(f"Creating event for funeraria: {funeraria}")
        serializer.save(created_by=self.request.user, funeraria=funeraria)

    def get_queryset(self):
        # Filter events to only those related to the user's funeraria
        user = self.request.user

        if not user.funeraria_id:
            print("User does not have an associated funeraria.")
            return Event.objects.none()

        funeraria = user.funeraria_id
        print(f"Fetching events for funeraria: {funeraria}")

        queryset = Event.objects.filter(funeraria=funeraria)
        print(f"Found {queryset.count()} events for funeraria: {funeraria}")
        return queryset

