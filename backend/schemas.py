from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MantenimientoOut(BaseModel):
    id_mantenimiento: int
    id_cisterna: int
    fecha: datetime
    tipo: str
    km_servicio: float
    proximo_km: float
    costo_soles: float
    estado: str

    class Config:
        from_attributes = True

class RegistroCombustibleCreate(BaseModel):
    id_cisterna: int
    km_odometro: Optional[float] = None
    galones_cargados: float
    precio_galon: Optional[float] = 16.50
    grifo: Optional[str] = "Grifo Primax Carretera Central"
    observaciones: Optional[str] = None

class RegistroCombustibleOut(BaseModel):
    id_registro: int
    id_cisterna: int
    fecha: datetime
    tipo: str
    km_odometro: Optional[float] = None
    km_gps_recorridos: float
    galones_cargados: float
    galones_estimados_gps: float
    precio_galon: float
    costo_total_soles: float
    grifo: str
    alerta_desvio: bool
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

class CisternaBase(BaseModel):
    placa: str
    chofer: str
    modelo_vehiculo: Optional[str] = "Volkswagen 13.180 Cabeza Ancha (Diésel)"
    rendimiento_km_galon: Optional[float] = 14.0
    capacidad_total_litros: Optional[int] = 10000
    litros_asignados: Optional[int] = 0
    litros_restantes: Optional[int] = 10000
    estado_ruta: Optional[str] = "En Base"
    sector_actual: Optional[str] = "Santa Anita"
    latitud_actual: Optional[float] = -12.0435
    longitud_actual: Optional[float] = -76.9698
    km_odometro: Optional[float] = 125400.0
    km_recorridos_hoy: Optional[float] = 0.0
    km_ultimo_mantenimiento: Optional[float] = 122000.0
    calidad_cloro_ppm: Optional[float] = 0.8
    calidad_ph: Optional[float] = 7.2

class CisternaOut(CisternaBase):
    id_cisterna: int
    activo: bool
    mantenimientos: Optional[List[MantenimientoOut]] = []

    class Config:
        from_attributes = True

class ClienteBase(BaseModel):
    nombre: str
    telefono: str
    dni_ruc: Optional[str] = None
    distrito: Optional[str] = "Santa Anita"
    sector: str
    manzana_lote: Optional[str] = None
    direccion_referencia: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    plus_code: Optional[str] = None
    token_acceso: Optional[str] = None
    saldo_deuda: Optional[float] = 0.0
    capacidad_tanque_litros: Optional[int] = 2000
    suscripcion_activa: Optional[bool] = False
    dias_suscripcion: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteOut(ClienteBase):
    id_cliente: int
    activo: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True

class PedidoCreate(BaseModel):
    id_cliente: int
    modalidad: Optional[str] = "Fraccionado"
    litros_agua: int = 2000
    total_soles: float
    metodo_pago: Optional[str] = "Efectivo"
    monto_pagado: Optional[float] = 0.0
    comprobante_tipo: Optional[str] = "Boleta"
    id_cisterna: Optional[int] = None
    notas_entrega: Optional[str] = None

class PedidoStatusUpdate(BaseModel):
    estado: str
    id_cisterna: Optional[int] = None
    monto_pagado: Optional[float] = None
    metodo_pago: Optional[str] = None
    notas_entrega: Optional[str] = None

class PedidoOut(BaseModel):
    id_pedido: int
    id_cliente: int
    id_cisterna: Optional[int] = None
    modalidad: str
    litros_agua: int
    fecha_pedido: datetime
    estado: str
    total_soles: float
    metodo_pago: str
    monto_pagado: float
    comprobante_tipo: str
    comprobante_numero: Optional[str] = None
    comision_chofer: float
    notas_entrega: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    cliente: Optional[ClienteOut] = None
    cisterna: Optional[CisternaOut] = None

    class Config:
        from_attributes = True

class SeguimientoCliente(BaseModel):
    cliente: ClienteOut
    pedido_activo: Optional[PedidoOut] = None
    cisterna_asignada: Optional[CisternaOut] = None
    historial_pedidos: List[PedidoOut] = []

class AsignacionCisterna(BaseModel):
    id_cisterna: int
    pedidos_ids: List[int]

class ResumenEstadisticas(BaseModel):
    total_ventas_hoy: float
    total_pedidos_hoy: int
    pedidos_pendientes: int
    pedidos_entregados: int
    litros_agua_despachados: int
    km_totales_flota_hoy: float
    gasto_combustible_estimado_soles: float
    galones_diesel_consumidos: float
    total_deuda_cobrar: float
    comisiones_choferes_acumuladas: float
