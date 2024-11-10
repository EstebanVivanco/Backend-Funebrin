from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Proveedor, ProductImage, ProductMovement
from .serializers import (
    ProductSerializer,
    ProveedorSerializer,
    ProductImageSerializer,
    ProductMovementSerializer
)
from utils.swagger_utils import CustomTags
from django.utils.timezone import now
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework import serializers


@CustomTags.inventary
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar productos por la funeraria del usuario autenticado
        funeraria = self.request.user.funeraria_id
        return Product.objects.filter(funeraria=funeraria)

    def perform_create(self, serializer):
        # Asignar la funeraria del usuario autenticado al crear un producto
        funeraria = self.request.user.funeraria_id
        if funeraria is None:
            raise serializers.ValidationError("El usuario no tiene una funeraria asociada.")
        return serializer.save(funeraria=funeraria)

    def create(self, request, *args, **kwargs):
        # Manejar la creación del producto junto con las imágenes
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.perform_create(serializer)

        # Manejar las imágenes
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        product_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        product_serializer.is_valid(raise_exception=True)
        self.perform_update(product_serializer)

        images_to_remove = request.data.get('images_to_remove', [])
        if images_to_remove:
            ProductImage.objects.filter(id__in=images_to_remove, product=instance).delete()

        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=instance, image=image)

        return Response(product_serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        funeraria = self.request.user.funeraria_id
        serializer.save(funeraria=funeraria)

    # Acción para obtener el total del precio de productos añadidos este mes
    @action(detail=False, methods=['get'], url_path='total-price-this-month')
    def total_price_this_month(self, request):
        current_date = now()
        first_day_of_month = current_date.replace(day=1)
        funeraria = request.user.funeraria_id

        if not funeraria:
            return Response({"error": "El usuario no tiene una funeraria asociada."}, status=status.HTTP_400_BAD_REQUEST)

        productos_mes = Product.objects.filter(
            funeraria=funeraria,
            date_added__gte=first_day_of_month,
            date_added__lte=current_date
        )

        total_price = productos_mes.aggregate(total=Sum('price'))['total'] or 0

        return Response({'total_price': total_price}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='external-products')
    def get_external_products(self, request):
        funeraria = self.request.user.funeraria_id
        print('>>>>>', self.request.user.funeraria_id)
        if not funeraria:
            return Response({"error": "El usuario no tiene una funeraria asociada."}, status=status.HTTP_400_BAD_REQUEST)

        external_products = Product.objects.filter(funeraria=funeraria, inventory_type='EX')
        
        if not external_products.exists():
            return Response({"message": "No se encontraron productos externos para la funeraria asociada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(external_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['get'], url_path='visible-external-products/(?P<funeraria_id>[^/.]+)')
    def get_visible_external_products(self, request, funeraria_id=None):
        # Validar que el ID de la funeraria fue proporcionado
        if not funeraria_id:
            return Response({"error": "Debe proporcionar el ID de la funeraria."}, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar productos externos y visibles para la funeraria especificada
        visible_external_products = Product.objects.filter(
            funeraria=funeraria_id,
            inventory_type='EX',
            visible=True
        )

        # Comprobar si hay productos que cumplen con el criterio
        if not visible_external_products.exists():
            return Response(
                {"message": "No se encontraron productos externos visibles para la funeraria especificada."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serializar y retornar los productos
        serializer = self.get_serializer(visible_external_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@CustomTags.productMovement
class ProductMovementViewSet(viewsets.ModelViewSet):
    serializer_class = ProductMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        funeraria = self.request.user.funeraria_id
        return ProductMovement.objects.filter(product__funeraria=funeraria)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        if product.funeraria != self.request.user.funeraria_id:
            raise serializers.ValidationError("No tienes permiso para agregar movimientos a este producto.")
        
        # Actualizar el stock del producto
        product.stock += quantity
        product.save()

        serializer.save()

    # Acción personalizada para obtener los movimientos de un producto específico
    @action(detail=False, methods=['get'], url_path='by-product/(?P<product_id>[^/.]+)')
    def get_movements_by_product(self, request, product_id=None):
        funeraria = request.user.funeraria_id
        
        try:
            product = Product.objects.get(id=product_id, funeraria=funeraria)
        except Product.DoesNotExist:
            return Response({"error": "Producto no encontrado o no tienes permiso para acceder a él."}, status=status.HTTP_404_NOT_FOUND)

        movements = ProductMovement.objects.filter(product=product)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@CustomTags.proveedor
class ProveedorViewSet(viewsets.ModelViewSet):
    serializer_class = ProveedorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Proveedor.objects.filter(funeraria=self.request.user.funeraria_id)

    def perform_create(self, serializer):
        funeraria = self.request.user.funeraria_id
        serializer.save(funeraria=funeraria)


