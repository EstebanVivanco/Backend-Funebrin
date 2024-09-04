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

    def create(self, request, *args, **kwargs):
        # Asegurarse de que la funeraria se asigne desde el usuario autenticado
        funeraria = request.user.funeraria_id

        # Agregar funeraria al validated_data antes de crear el producto
        product_serializer = self.get_serializer(data=request.data)
        product_serializer.is_valid(raise_exception=True)
        product = product_serializer.save(funeraria=funeraria)

        # Manejo de las imágenes
        images = request.FILES.getlist('images')  # Cambia 'images' por el nombre de tu campo de imágenes
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        headers = self.get_success_headers(product_serializer.data)
        return Response(product_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
