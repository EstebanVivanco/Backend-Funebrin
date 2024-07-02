from drf_spectacular.utils import extend_schema

class CustomTags:
    # Cuentas
    accounts = extend_schema(tags=['Cuentas'])
    

    # Inventario (productos)
    inventary = extend_schema(tags=['Inventario / Productos'])

      # Inventario (productos)
    typeProduct = extend_schema(tags=['Tipo de producto'])
