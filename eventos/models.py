from django.db import models
from django.conf import settings
from accounts.models import Funeraria  # Import Funeraria directly
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('personal', 'Personal'),  # Event for the person creating it
        ('company', 'Company'),    # Event for all assigned workers
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    funeraria = models.ForeignKey(Funeraria, on_delete=models.CASCADE)  # Use the direct import reference

    def __str__(self):
        return self.title

class EventAssignment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='assignments')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_events')

    def __str__(self):
        return f"{self.worker.username} assigned to {self.event.title}"
