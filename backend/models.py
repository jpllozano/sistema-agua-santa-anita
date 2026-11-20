from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Cliente(Base):
    __tablename__ = "Clientes"

    id_cliente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    telefono = Column(String(25), nullable=False, index=True, unique=True)
    dni_ruc = Column(String(20), nullable=True) # Para facturación electrónica SUNAT
    distrito = Column(String(100), default="Santa Anita")
    sector = Column(String(100), nullable=False, index=True) # Coop. Universal, Huáscar, Nocheto, etc.
    manzana_lote = Column(String(50), nullable=True)
    direccion_referencia = Column(String(300), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    plus_code = Column(String(50), nullable=True)
    token_acceso = Column(String(64), unique=True, index=True)
    saldo_deuda = Column(Float, default=0.0)
    capacidad_tanque_litros = Column(Integer, default=2000) # Tanque elevado o cisterna propia
    suscripcion_activa = Column(Boolean, default=False)     # Recarga periódica automática
    dias_suscripcion = Column(String(100), nullable=True)   # Ej: 'Lunes y Jueves'
    notas = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    pedidos = relationship("Pedido", back_populates="cliente")

class Cisterna(Base):
    __tablename__ = "Cisternas"

    id_cisterna = Column(Integer, primary_key=True, index=True, autoincrement=True)
    placa = Column(String(20), unique=True, nullable=False)
    chofer = Column(String(100), nullable=False)
    modelo_vehiculo = Column(String(100), default="Volkswagen 13.180 Cabeza Ancha (Diésel)")
    rendimiento_km_galon = Column(Float, default=14.0) # Km promedio por galón en subidas/ciudad
    capacidad_total_litros = Column(Integer, default=10000) # 10,000 Litros estándar
    litros_asignados = Column(Integer, default=0)
    litros_restantes = Column(Integer, default=10000)
    estado_ruta = Column(String(30), default="En Base") # 'En Base', 'En Ruta', 'Descargando'
    sector_actual = Column(String(100), default="Santa Anita")
    latitud_actual = Column(Float, default=-12.0435)
    longitud_actual = Column(Float, default=-76.9698)
    km_odometro = Column(Float, default=125400.0)      # Odómetro acumulado
    km_recorridos_hoy = Column(Float, default=0.0)     # Calculado por GPS
    km_ultimo_mantenimiento = Column(Float, default=122000.0) # Alerta cada 5,000 km
    calidad_cloro_ppm = Column(Float, default=0.8)     # Nivel cloro residual (0.5 - 1.0 estándar)
    calidad_ph = Column(Float, default=7.2)
    activo = Column(Boolean, default=True)

    pedidos = relationship("Pedido", back_populates="cisterna")
    registros_combustible = relationship("RegistroCombustible", back_populates="cisterna")
    mantenimientos = relationship("MantenimientoVehiculo", back_populates="cisterna")

class Pedido(Base):
    __tablename__ = "Pedidos"

    id_pedido = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("Clientes.id_cliente"), nullable=False)
    id_cisterna = Column(Integer, ForeignKey("Cisternas.id_cisterna"), nullable=True)
    modalidad = Column(String(30), default="Fraccionado") # 'Cisterna Completa' (10,000L) o 'Fraccionado' (1,500L, 2,000L, 3,000L)
    litros_agua = Column(Integer, nullable=False, default=2000)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, index=True)
    estado = Column(String(30), default="Pendiente", index=True) # Pendiente, En camino, Llegando, Entregado, Cancelado
    total_soles = Column(Float, nullable=False)
    metodo_pago = Column(String(30), default="Efectivo") # 'Efectivo', 'Yape', 'Plin', 'Credito'
    monto_pagado = Column(Float, default=0.0)
    comprobante_tipo = Column(String(20), default="Boleta") # 'Boleta', 'Factura', 'Nota'
    comprobante_numero = Column(String(30), nullable=True) # Serie B001-000412
    comision_chofer = Column(Float, default=15.0) # Comisión fija o por volumen (S/.)
    notas_entrega = Column(String(300), nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)

    cliente = relationship("Cliente", back_populates="pedidos")
    cisterna = relationship("Cisterna", back_populates="pedidos")

class RegistroCombustible(Base):
    __tablename__ = "RegistrosCombustible"

    id_registro = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cisterna = Column(Integer, ForeignKey("Cisternas.id_cisterna"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, index=True)
    tipo = Column(String(30), default="Recarga Grifo")
    km_odometro = Column(Float, nullable=True)
    km_gps_recorridos = Column(Float, default=0.0)
    galones_cargados = Column(Float, default=0.0)
    galones_estimados_gps = Column(Float, default=0.0)
    precio_galon = Column(Float, default=16.50) # Precio Diésel
    costo_total_soles = Column(Float, default=0.0)
    grifo = Column(String(100), default="Primax Carretera Central / Santa Anita")
    alerta_desvio = Column(Boolean, default=False)
    observaciones = Column(String(300), nullable=True)

    cisterna = relationship("Cisterna", back_populates="registros_combustible")

class MantenimientoVehiculo(Base):
    __tablename__ = "MantenimientosVehiculo"

    id_mantenimiento = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cisterna = Column(Integer, ForeignKey("Cisternas.id_cisterna"), nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(50), nullable=False) # 'Cambio de Aceite', 'Bomba de Agua Cisterna', 'Frenos', 'Válvulas'
    km_servicio = Column(Float, nullable=False)
    proximo_km = Column(Float, nullable=False)
    costo_soles = Column(Float, default=0.0)
    taller = Column(String(100), default="Taller Mecánico Diésel Santa Anita")
    estado = Column(String(20), default="Realizado")

    cisterna = relationship("Cisterna", back_populates="mantenimientos")
