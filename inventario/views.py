from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ProductType, Proveedor, ProductImage
from .serializers import ProductSerializer, TypeProductSerializer, ProveedorSerializer, ProductImageSerializer
from utils.swagger_utils import CustomTags

@CustomTags.inventary
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)  # Asegúrate de que estas clases estén aquí
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Guardar el producto
        product_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        product_serializer.is_valid(raise_exception=True)
        self.perform_update(product_serializer)

        # Eliminar imágenes si se envían para eliminar
        images_to_remove = request.data.get('images_to_remove', '')
        if images_to_remove:
            images_to_remove_list = images_to_remove.split(',')
            ProductImage.objects.filter(id__in=images_to_remove_list, product=instance).delete()

        # Guardar nuevas imágenes
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=instance, image=image)

        return Response(product_serializer.data, status=status.HTTP_200_OK)

@CustomTags.proveedor
class ProveedorViewSet(viewsets.ModelViewSet):
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filtrar proveedores por la funeraria del usuario autenticado
        return Proveedor.objects.filter(funeraria=self.request.user.funeraria_id)

    def perform_create(self, serializer):
        # Obtiene la funeraria del usuario autenticado
        funeraria = self.request.user.funeraria_id
        serializer.save(funeraria=funeraria)

@CustomTags.typeProduct
class TypeProductViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    serializer_class = TypeProductSerializer
