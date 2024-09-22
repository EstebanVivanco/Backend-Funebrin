from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ProductType, Proveedor, ProductImage
from .serializers import ProductSerializer, TypeProductSerializer, ProveedorSerializer, ProductImageSerializer
from utils.swagger_utils import CustomTags
from django.utils.timezone import now
from django.db.models import Sum
from rest_framework.decorators import action


@CustomTags.inventary
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)  # Asegúrate de que estas clases estén aquí
    permission_classes = [IsAuthenticated]

    
     # Nueva acción para obtener el total del precio de productos añadidos este mes
    @action(detail=False, methods=['get'], url_path='total-price-this-month')
    def total_price_this_month(self, request):
        # Obtener la fecha actual y el primer día del mes
        current_date = now()
        first_day_of_month = current_date.replace(day=1)
        
        # Obtener la funeraria asociada al usuario autenticado
        funeraria = request.user.funeraria_id

        # Asegurar que el usuario tiene una funeraria asociada
        if not funeraria:
            return Response({"error": "El usuario no tiene una funeraria asociada."}, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar los productos añadidos este mes que pertenezcan a la funeraria del usuario autenticado
        productos_mes = Product.objects.filter(
            funeraria=funeraria,  # Filtrar por funeraria
            date_added__gte=first_day_of_month,
            date_added__lte=current_date
        )
        
        # Sumar los precios de los productos
        total_price = productos_mes.aggregate(total=Sum('price'))['total'] or 0

        return Response({
            'total_price': total_price
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        product_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        product_serializer.is_valid(raise_exception=True)
        self.perform_update(product_serializer)

        images_to_remove = request.data.get('images_to_remove', '')
        if images_to_remove:
            images_to_remove_list = images_to_remove.split(',')
            ProductImage.objects.filter(id__in=images_to_remove_list, product=instance).delete()

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
