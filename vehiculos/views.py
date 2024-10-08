from rest_framework import viewsets
from .serializers import VehicleSerializer, TypeVehicleSerializer
from .models import Vehicle, VehicleType, VehicleImage, VehicleDocument
from utils.swagger_utils import CustomTags
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

@CustomTags.vehicles
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Guardar el vehículo
        vehicle_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        vehicle_serializer.is_valid(raise_exception=True)
        self.perform_update(vehicle_serializer)

        # Eliminar imágenes si se envían para eliminar
        images_to_remove = vehicle_serializer.validated_data.get('images_to_remove', [])
        if images_to_remove:
            VehicleImage.objects.filter(id__in=images_to_remove, vehicle=instance).delete()

        # Eliminar documentos si se envían para eliminar
        documents_to_remove = vehicle_serializer.validated_data.get('documents_to_remove', [])
        if documents_to_remove:
            VehicleDocument.objects.filter(id__in=documents_to_remove, vehicle=instance).delete()

        # Guardar nuevas imágenes
        images = request.FILES.getlist('images')
        for image in images:
            VehicleImage.objects.create(vehicle=instance, image=image)

        # Guardar nuevos documentos con títulos
        documents = request.FILES.getlist('documents')
        titles = request.data.getlist('titles', [])
        for index, document in enumerate(documents):
            title = titles[index] if index < len(titles) else 'Documento sin título'
            VehicleDocument.objects.create(vehicle=instance, document=document, title=title)

        return Response(vehicle_serializer.data, status=status.HTTP_200_OK)
    
@CustomTags.typeVehicle
class TypeVehicleViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = TypeVehicleSerializer
