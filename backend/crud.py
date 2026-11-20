import uuid
import math
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
import schemas

def generar_token():
    return uuid.uuid4().hex[:10]

def generar_numero_comprobante(tipo: str, id_pedido: int):
    prefijo = "B001" if tipo == "Boleta" else "F001"
    return f"{prefijo}-{str(id_pedido).zfill(6)}"

def distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en kilómetros entre dos coordenadas GPS."""
    if not (lat1 and lon1 and lat2 and lon2):
        return 0.0
    R = 6371.0 # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def get_clientes(db: Session, search: str = None, sector: str = None):
    query = db.query(models.Cliente).filter(models.Cliente.activo == True)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Cliente.nombre.ilike(search_fmt),
                models.Cliente.telefono.ilike(search_fmt),
                models.Cliente.direccion_referencia.ilike(search_fmt),
                models.Cliente.manzana_lote.ilike(search_fmt)
            )
        )
    if sector and sector != "Todos":
        query = query.filter(models.Cliente.sector == sector)
    return query.order_by(models.Cliente.nombre.asc()).all()

def get_cliente(db: Session, id_cliente: int):
    return db.query(models.Cliente).filter(models.Cliente.id_cliente == id_cliente).first()

def get_cliente_by_phone(db: Session, telefono: str):
    clean_phone = telefono.strip().replace(" ", "").replace("+51", "")
    return db.query(models.Cliente).filter(
        or_(
            models.Cliente.telefono == clean_phone,
            models.Cliente.telefono == f"+51{clean_phone}"
        )
    ).first()

def get_cliente_by_token(db: Session, token: str):
    return db.query(models.Cliente).filter(models.Cliente.token_acceso == token).first()

def create_cliente(db: Session, cliente_in: schemas.ClienteCreate):
    data = cliente_in.dict()
    if not data.get("token_acceso"):
        data["token_acceso"] = generar_token()
    db_cliente = models.Cliente(**data)
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def get_cisternas(db: Session):
    return db.query(models.Cisterna).filter(models.Cisterna.activo == True).all()

def get_cisterna(db: Session, id_cisterna: int):
    return db.query(models.Cisterna).filter(models.Cisterna.id_cisterna == id_cisterna).first()

def update_cisterna_ubicacion(db: Session, id_cisterna: int, lat: float, lng: float, sector: str = None):
    cisterna = get_cisterna(db, id_cisterna)
    if cisterna:
        # Calcular delta de distancia GPS recorrida
        delta_km = distancia_haversine(cisterna.latitud_actual, cisterna.longitud_actual, lat, lng)
        if delta_km > 0.05: # Movimiento superior a 50 metros
            cisterna.km_recorridos_hoy += delta_km
            cisterna.km_odometro += delta_km

        cisterna.latitud_actual = lat
        cisterna.longitud_actual = lng
        if sector:
            cisterna.sector_actual = sector
        db.commit()
        db.refresh(cisterna)
    return cisterna

def get_pedidos(db: Session, estado: str = None):
    query = db.query(models.Pedido)
    if estado and estado != "Todos":
        query = query.filter(models.Pedido.estado == estado)
    return query.order_by(models.Pedido.fecha_pedido.desc()).all()

def get_pedido(db: Session, id_pedido: int):
    return db.query(models.Pedido).filter(models.Pedido.id_pedido == id_pedido).first()

def create_pedido(db: Session, pedido_in: schemas.PedidoCreate):
    db_pedido = models.Pedido(
        id_cliente=pedido_in.id_cliente,
        id_cisterna=pedido_in.id_cisterna,
        modalidad=pedido_in.modalidad,
        litros_agua=pedido_in.litros_agua,
        fecha_pedido=datetime.utcnow(),
        estado="Pendiente",
        total_soles=pedido_in.total_soles,
        metodo_pago=pedido_in.metodo_pago,
        monto_pagado=pedido_in.monto_pagado,
        comprobante_tipo=pedido_in.comprobante_tipo or "Boleta",
        comision_chofer=20.0 if pedido_in.modalidad == "Cisterna Completa" else 15.0,
        notas_entrega=pedido_in.notas_entrega
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)

    db_pedido.comprobante_numero = generar_numero_comprobante(db_pedido.comprobante_tipo, db_pedido.id_pedido)

    if pedido_in.id_cisterna:
        cisterna = get_cisterna(db, pedido_in.id_cisterna)
        if cisterna:
            cisterna.litros_asignados += pedido_in.litros_agua
            cisterna.litros_restantes = max(0, cisterna.capacidad_total_litros - cisterna.litros_asignados)

    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def update_pedido_status(db: Session, id_pedido: int, status_in: schemas.PedidoStatusUpdate):
    db_pedido = get_pedido(db, id_pedido)
    if not db_pedido:
        return None

    prev_estado = db_pedido.estado
    db_pedido.estado = status_in.estado

    if status_in.id_cisterna is not None:
        db_pedido.id_cisterna = status_in.id_cisterna
    if status_in.monto_pagado is not None:
        db_pedido.monto_pagado = status_in.monto_pagado
    if status_in.metodo_pago is not None:
        db_pedido.metodo_pago = status_in.metodo_pago
    if status_in.notas_entrega is not None:
        db_pedido.notas_entrega = status_in.notas_entrega

    if status_in.estado == "Entregado" and prev_estado != "Entregado":
        db_pedido.fecha_entrega = datetime.utcnow()
        cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == db_pedido.id_cliente).first()
        if cliente:
            monto_real = status_in.monto_pagado if status_in.monto_pagado is not None else db_pedido.monto_pagado
            deuda = max(0.0, db_pedido.total_soles - monto_real)
            if deuda > 0:
                cliente.saldo_deuda += deuda

    db.commit()
    db.refresh(db_pedido)
    return db_pedido

def asignar_pedidos_a_cisterna(db: Session, id_cisterna: int, pedidos_ids: list):
    cisterna = get_cisterna(db, id_cisterna)
    if not cisterna:
        return None

    litros_totales = 0
    for pid in pedidos_ids:
        p = get_pedido(db, pid)
        if p:
            p.id_cisterna = id_cisterna
            p.estado = "En camino"
            litros_totales += p.litros_agua

    cisterna.litros_asignados = litros_totales
    cisterna.litros_restantes = max(0, cisterna.capacidad_total_litros - litros_totales)
    cisterna.estado_ruta = "En Ruta"
    db.commit()
    db.refresh(cisterna)
    return cisterna

# ----------------- GESTIÓN DE COMBUSTIBLE PARA CAMIONES ANTIGUOS -----------------

def registrar_combustible(db: Session, recarga_in: schemas.RegistroCombustibleCreate):
    cisterna = get_cisterna(db, recarga_in.id_cisterna)
    if not cisterna:
        return None

    km_gps = cisterna.km_recorridos_hoy
    rendimiento = cisterna.rendimiento_km_galon or 14.0
    galones_esperados = round(km_gps / rendimiento, 2) if km_gps > 0 else 0.0

    # Detectar alerta de anomalía o desvío de combustible (> 20% de diferencia)
    alerta = False
    if galones_esperados > 0:
        diferencia = recarga_in.galones_cargados - galones_esperados
        if diferencia > (galones_esperados * 0.20):
            alerta = True

    costo_total = round(recarga_in.galones_cargados * (recarga_in.precio_galon or 16.50), 2)

    registro = models.RegistroCombustible(
        id_cisterna=recarga_in.id_cisterna,
        fecha=datetime.utcnow(),
        tipo="Recarga Grifo",
        km_odometro=recarga_in.km_odometro or cisterna.km_odometro,
        km_gps_recorridos=km_gps,
        galones_cargados=recarga_in.galones_cargados,
        galones_estimados_gps=galones_esperados,
        precio_galon=recarga_in.precio_galon or 16.50,
        costo_total_soles=costo_total,
        grifo=recarga_in.grifo or "Grifo Primax Carretera Central",
        alerta_desvio=alerta,
        observaciones=recarga_in.observaciones
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro

def get_registros_combustible(db: Session, id_cisterna: int = None):
    query = db.query(models.RegistroCombustible)
    if id_cisterna:
        query = query.filter(models.RegistroCombustible.id_cisterna == id_cisterna)
    return query.order_by(models.RegistroCombustible.fecha.desc()).all()

def get_mantenimientos(db: Session, id_cisterna: int = None):
    query = db.query(models.MantenimientoVehiculo)
    if id_cisterna:
        query = query.filter(models.MantenimientoVehiculo.id_cisterna == id_cisterna)
    return query.order_by(models.MantenimientoVehiculo.fecha.desc()).all()

def get_seguimiento_cliente(db: Session, identificador: str):
    cliente = get_cliente_by_token(db, identificador)
    if not cliente:
        cliente = get_cliente_by_phone(db, identificador)
    if not cliente:
        return None

    pedidos_todos = db.query(models.Pedido).filter(models.Pedido.id_cliente == cliente.id_cliente).order_by(models.Pedido.fecha_pedido.desc()).all()
    
    pedido_activo = next((p for p in pedidos_todos if p.estado in ["Pendiente", "En camino", "Llegando"]), None)
    if not pedido_activo and pedidos_todos:
        pedido_activo = pedidos_todos[0]

    cisterna_asignada = None
    if pedido_activo and pedido_activo.id_cisterna:
        cisterna_asignada = get_cisterna(db, pedido_activo.id_cisterna)

    return schemas.SeguimientoCliente(
        cliente=cliente,
        pedido_activo=pedido_activo,
        cisterna_asignada=cisterna_asignada,
        historial_pedidos=pedidos_todos[:5]
    )

def get_dashboard_stats(db: Session):
    pedidos_todos = db.query(models.Pedido).all()
    clientes_todos = db.query(models.Cliente).filter(models.Cliente.activo == True).all()
    cisternas_todas = db.query(models.Cisterna).filter(models.Cisterna.activo == True).all()

    total_ventas = sum(p.total_soles for p in pedidos_todos if p.estado == "Entregado")
    total_pedidos = len(pedidos_todos)
    pedidos_pendientes = len([p for p in pedidos_todos if p.estado in ["Pendiente", "En camino", "Llegando"]])
    pedidos_entregados = len([p for p in pedidos_todos if p.estado == "Entregado"])
    
    litros_agua = sum(p.litros_agua for p in pedidos_todos if p.estado == "Entregado")
    km_totales = sum(c.km_recorridos_hoy for c in cisternas_todas)
    
    # Consumo Diésel estimado: km / 14 km/galon
    galones_diesel = round(km_totales / 14.0, 1) if km_totales > 0 else 0.0
    gasto_combustible = round(galones_diesel * 16.50, 2)

    total_deuda = sum(c.saldo_deuda for c in clientes_todos)
    comisiones = sum(p.comision_chofer for p in pedidos_todos if p.estado == "Entregado")

    return schemas.ResumenEstadisticas(
        total_ventas_hoy=total_ventas,
        total_pedidos_hoy=total_pedidos,
        pedidos_pendientes=pedidos_pendientes,
        pedidos_entregados=pedidos_entregados,
        litros_agua_despachados=litros_agua,
        km_totales_flota_hoy=round(km_totales, 1),
        gasto_combustible_estimado_soles=gasto_combustible,
        galones_diesel_consumidos=galones_diesel,
        total_deuda_cobrar=total_deuda,
        comisiones_choferes_acumuladas=comisiones
    )

def seed_initial_data(db: Session):
    if db.query(models.Cisterna).first():
        return {"message": "Datos ya cargados"}

    # Cisternas Volkswagen Cabeza Ancha (10,000 Litros)
    c1 = models.Cisterna(
        placa="EGB-421",
        chofer="Don Pedro Quispe",
        modelo_vehiculo="Volkswagen 13.180 Cabeza Ancha (Diésel)",
        rendimiento_km_galon=13.5,
        capacidad_total_litros=10000,
        litros_asignados=6000,
        litros_restantes=4000,
        estado_ruta="En Ruta",
        sector_actual="Coop. Huáscar",
        latitud_actual=-12.040100,
        longitud_actual=-76.964500,
        km_odometro=142850.0,
        km_recorridos_hoy=28.5,
        km_ultimo_mantenimiento=140000.0,
        calidad_cloro_ppm=0.85,
        calidad_ph=7.2
    )
    c2 = models.Cisterna(
        placa="F2T-819",
        chofer="Lucho Ramos",
        modelo_vehiculo="Volkswagen Worker 15.180 Cabeza Ancha",
        rendimiento_km_galon=14.0,
        capacidad_total_litros=10000,
        litros_asignados=10000,
        litros_restantes=0,
        estado_ruta="En Ruta",
        sector_actual="Coop. Universal",
        latitud_actual=-12.043900,
        longitud_actual=-76.968900,
        km_odometro=189200.0,
        km_recorridos_hoy=41.2,
        km_ultimo_mantenimiento=185000.0,
        calidad_cloro_ppm=0.90,
        calidad_ph=7.3
    )
    db.add_all([c1, c2])
    db.commit()

    # Mantenimientos Preventivos de Flota
    m1 = models.MantenimientoVehiculo(
        id_cisterna=1,
        fecha=datetime.utcnow(),
        tipo="Cambio de Aceite 15W40 y Filtros Diésel",
        km_servicio=140000.0,
        proximo_km=145000.0,
        costo_soles=420.0,
        taller="Taller Camiones Santa Anita",
        estado="Al día"
    )
    m2 = models.MantenimientoVehiculo(
        id_cisterna=2,
        fecha=datetime.utcnow(),
        tipo="Engrase de Válvulas y Mangueras de Descarga",
        km_servicio=185000.0,
        proximo_km=190000.0,
        costo_soles=180.0,
        taller="Servicio Hidráulico Santa Anita",
        estado="Al día"
    )
    db.add_all([m1, m2])
    db.commit()

    # Registros de Combustible (Diésel)
    rc1 = models.RegistroCombustible(
        id_cisterna=1,
        fecha=datetime.utcnow(),
        tipo="Recarga Grifo",
        km_odometro=142821.5,
        km_gps_recorridos=28.5,
        galones_cargados=2.2,
        galones_estimados_gps=2.1,
        precio_galon=16.50,
        costo_total_soles=36.30,
        grifo="Primax Ovalo Santa Anita",
        alerta_desvio=False,
        observaciones="Rendimiento normal en subida a Huáscar"
    )
    db.add(rc1)
    db.commit()

    # Clientes Residenciales y Comerciales de Agua Potable
    clientes_seed = [
        models.Cliente(
            nombre="Sr. Carlos Mendoza",
            telefono="955443322",
            dni_ruc="10458921",
            distrito="Santa Anita",
            sector="Coop. Huáscar",
            manzana_lote="Mz. B2 Lote 5",
            direccion_referencia="Subiendo por la escalera 3 de Huáscar, casa amarilla con portón de madera",
            latitud=-12.039870,
            longitud=-76.963210,
            plus_code="75W3+XX Santa Anita",
            token_acceso="carlos-h19",
            saldo_deuda=25.0,
            capacidad_tanque_litros=2000,
            suscripcion_activa=True,
            dias_suscripcion="Lunes y Jueves (2,000 L)",
            notas="Requiere 30 metros de manguera. Subida peatonal."
        ),
        models.Cliente(
            nombre="Vecina Juana Alarcón",
            telefono="944112233",
            dni_ruc="41258934",
            distrito="Santa Anita",
            sector="Coop. Huáscar",
            manzana_lote="Mz. B2 Lote 8",
            direccion_referencia="A 3 casas del Sr. Carlos, portón negro con timbre blanco",
            latitud=-12.039600,
            longitud=-76.963000,
            plus_code="75W3+XY Santa Anita",
            token_acceso="juana-h22",
            saldo_deuda=0.0,
            capacidad_tanque_litros=2000,
            suscripcion_activa=False,
            notas="Comparte manguera con Don Carlos para llenado conjunto."
        ),
        models.Cliente(
            nombre="Lavandería Industrial Santa Anita",
            telefono="991223344",
            dni_ruc="20601234567", # RUC para Factura
            distrito="Santa Anita",
            sector="Av. Los Ruiseñores",
            manzana_lote="N° 450",
            direccion_referencia="Al costado de Inkafarma, local con portón corredizo",
            latitud=-12.046890,
            longitud=-76.973410,
            plus_code="75W3+4C Santa Anita",
            token_acceso="lav-r45",
            saldo_deuda=0.0,
            capacidad_tanque_litros=10000,
            suscripcion_activa=True,
            dias_suscripcion="Diario (Cisterna Completa 10,000 L)",
            notas="Solicita Factura Electrónica y certificado de cloro."
        ),
        models.Cliente(
            nombre="Doña Rosa Quispe",
            telefono="987654321",
            dni_ruc="08954122",
            distrito="Santa Anita",
            sector="Coop. Universal",
            manzana_lote="Mz. F Lote 12",
            direccion_referencia="Frente a la loza deportiva de Universal, casa de 3 pisos con reja azul",
            latitud=-12.043512,
            longitud=-76.969820,
            plus_code="75W3+9C Santa Anita",
            token_acceso="rosa-u42",
            saldo_deuda=0.0,
            capacidad_tanque_litros=2000,
            suscripcion_activa=True,
            dias_suscripcion="Miércoles y Sábados (2,000 L)",
            notas="Tanque de polietileno en el techo. Paga por Yape."
        )
    ]
    db.add_all(clientes_seed)
    db.commit()

    # Pedidos iniciales de Agua Potable
    p1 = models.Pedido(
        id_cliente=1,
        id_cisterna=1,
        modalidad="Fraccionado",
        litros_agua=2000,
        estado="En camino",
        total_soles=50.0,
        metodo_pago="Yape",
        monto_pagado=50.0,
        comprobante_tipo="Boleta",
        comprobante_numero="B001-000101",
        comision_chofer=15.0,
        notas_entrega="Cisterna subiendo por Huáscar con manguera lista"
    )
    p2 = models.Pedido(
        id_cliente=2,
        id_cisterna=1,
        modalidad="Fraccionado",
        litros_agua=2000,
        estado="En camino",
        total_soles=50.0,
        metodo_pago="Efectivo",
        monto_pagado=0.0,
        comprobante_tipo="Boleta",
        comprobante_numero="B001-000102",
        comision_chofer=15.0,
        notas_entrega="Descargar inmediatamente después del Sr. Carlos"
    )
    p3 = models.Pedido(
        id_cliente=3,
        id_cisterna=2,
        modalidad="Cisterna Completa",
        litros_agua=10000,
        estado="En camino",
        total_soles=240.0,
        metodo_pago="Efectivo",
        monto_pagado=240.0,
        comprobante_tipo="Factura",
        comprobante_numero="F001-000055",
        comision_chofer=30.0,
        notas_entrega="Descarga por gravedad directa a pozo subterráneo"
    )
    db.add_all([p1, p2, p3])
    db.commit()
    return {"message": "Datos de Agua, Combustible y Flota inicializados"}
