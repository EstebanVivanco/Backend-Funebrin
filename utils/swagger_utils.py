from drf_spectacular.utils import extend_schema

class CustomTags:
    # Cuentas
    accounts = extend_schema(tags=['Cuentas'])
    
    # Trabajadores
    trabajadores = extend_schema(tags=['Cuentas'])

    # Inventario (productos)
    inventary = extend_schema(tags=['Inventario / Productos'])

    # Inventario (productos)
    typeProduct = extend_schema(tags=['Tipo de producto'])

    # Vehiculos
    vehicles = extend_schema(tags=['Vehiculos'])

    # Tipo de vehiculos
    typeVehicle = extend_schema(tags=['Tipo de vehiculos'])

    # Cliente
    cliente = extend_schema(tags=['Clientes'])

    # Tipo Cliente
    tipoCliente = extend_schema(tags=['Tipo de Cliente'])
    
    
    proveedor = extend_schema(tags=['Proveedor'])
    
    documentos = extend_schema(tags=['documentos'])
    
    velatorios = extend_schema(tags=['velatorios'])
    
    contrato = extend_schema(tags=['contrato'])
    
    cliente = extend_schema(tags=['cliente'])
    
    fallecido = extend_schema(tags=['fallecido'])
    
    productMovement = extend_schema(tags=['productMovement'])
    
    