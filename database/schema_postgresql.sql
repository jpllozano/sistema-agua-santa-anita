-- ============================================================================
-- BASE DE DATOS: AguaSantaAnitaDB (PostgreSQL 12+)
-- SISTEMA DE GESTIÓN DE CISTERNAS, DESPACHO FRACCIONADO Y CONTROL DE FLOTA
-- Compatible con: PostgreSQL 12+, Supabase, Neon, AWS RDS PostgreSQL
-- ============================================================================

-- Limpiar tablas previas en cascada
DROP TABLE IF EXISTS MantenimientosVehiculo CASCADE;
DROP TABLE IF EXISTS RegistrosCombustible CASCADE;
DROP TABLE IF EXISTS Pedidos CASCADE;
DROP TABLE IF EXISTS Clientes CASCADE;
DROP TABLE IF EXISTS Cisternas CASCADE;

-- 1. TABLA: Cisternas (Flota Volkswagen 13.180 Cabeza Ancha)
CREATE TABLE Cisternas (
    id_cisterna SERIAL PRIMARY KEY,
    placa VARCHAR(20) UNIQUE NOT NULL,
    chofer VARCHAR(100) NOT NULL,
    modelo_vehiculo VARCHAR(100) DEFAULT 'Volkswagen 13.180 Cabeza Ancha (Diésel)',
    rendimiento_km_galon NUMERIC(5, 2) DEFAULT 14.00,
    capacidad_total_litros INT DEFAULT 10000,
    litros_asignados INT DEFAULT 0,
    litros_restantes INT DEFAULT 10000,
    estado_ruta VARCHAR(30) DEFAULT 'En Base',
    sector_actual VARCHAR(100) DEFAULT 'Santa Anita',
    latitud_actual NUMERIC(10, 8) DEFAULT -12.043500,
    longitud_actual NUMERIC(11, 8) DEFAULT -76.969800,
    km_odometro NUMERIC(10, 1) DEFAULT 125400.0,
    km_recorridos_hoy NUMERIC(8, 2) DEFAULT 0.00,
    km_ultimo_mantenimiento NUMERIC(10, 1) DEFAULT 122000.0,
    calidad_cloro_ppm NUMERIC(4, 2) DEFAULT 0.85,
    calidad_ph NUMERIC(4, 2) DEFAULT 7.20,
    activo BOOLEAN DEFAULT TRUE
);

-- 2. TABLA: Clientes y Vecinos de Santa Anita
CREATE TABLE Clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(25) NOT NULL UNIQUE,
    dni_ruc VARCHAR(20) NULL,
    distrito VARCHAR(100) DEFAULT 'Santa Anita',
    sector VARCHAR(100) NOT NULL,
    manzana_lote VARCHAR(50) NULL,
    direccion_referencia VARCHAR(300) NOT NULL,
    latitud NUMERIC(10, 8) NULL,
    longitud NUMERIC(11, 8) NULL,
    plus_code VARCHAR(50) NULL,
    token_acceso VARCHAR(64) UNIQUE NOT NULL,
    saldo_deuda NUMERIC(10, 2) DEFAULT 0.00,
    capacidad_tanque_litros INT DEFAULT 2000,
    suscripcion_activa BOOLEAN DEFAULT FALSE,
    dias_suscripcion VARCHAR(100) NULL,
    notas TEXT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: Pedidos de Agua (Despacho Fraccionado o Cisterna Completa)
CREATE TABLE Pedidos (
    id_pedido SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL REFERENCES Clientes(id_cliente) ON DELETE CASCADE,
    id_cisterna INT NULL REFERENCES Cisternas(id_cisterna) ON DELETE SET NULL,
    modalidad VARCHAR(30) DEFAULT 'Fraccionado',
    litros_agua INT NOT NULL DEFAULT 2000,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'Pendiente',
    total_soles NUMERIC(10, 2) NOT NULL,
    metodo_pago VARCHAR(30) DEFAULT 'Efectivo',
    monto_pagado NUMERIC(10, 2) DEFAULT 0.00,
    comprobante_tipo VARCHAR(20) DEFAULT 'Boleta',
    comprobante_numero VARCHAR(30) NULL,
    comision_chofer NUMERIC(10, 2) DEFAULT 15.00,
    notas_entrega VARCHAR(300) NULL,
    fecha_entrega TIMESTAMP NULL
);

-- 4. TABLA: Control de Combustible (Diésel por GPS y Grifo)
CREATE TABLE RegistrosCombustible (
    id_registro SERIAL PRIMARY KEY,
    id_cisterna INT NOT NULL REFERENCES Cisternas(id_cisterna) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(30) DEFAULT 'Recarga Grifo',
    km_odometro NUMERIC(10, 1) NULL,
    km_gps_recorridos NUMERIC(8, 2) DEFAULT 0.00,
    galones_cargados NUMERIC(6, 2) NOT NULL,
    galones_estimados_gps NUMERIC(6, 2) DEFAULT 0.00,
    precio_galon NUMERIC(6, 2) DEFAULT 16.50,
    costo_total_soles NUMERIC(10, 2) NOT NULL,
    grifo VARCHAR(100) DEFAULT 'Primax Santa Anita',
    alerta_desvio BOOLEAN DEFAULT FALSE,
    observaciones VARCHAR(300) NULL
);

-- 5. TABLA: Mantenimiento Preventivo de Flota
CREATE TABLE MantenimientosVehiculo (
    id_mantenimiento SERIAL PRIMARY KEY,
    id_cisterna INT NOT NULL REFERENCES Cisternas(id_cisterna) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(100) NOT NULL,
    km_servicio NUMERIC(10, 1) NOT NULL,
    proximo_km NUMERIC(10, 1) NOT NULL,
    costo_soles NUMERIC(10, 2) DEFAULT 0.00,
    taller VARCHAR(100) DEFAULT 'Taller Camiones Santa Anita',
    estado VARCHAR(20) DEFAULT 'Al día'
);

-- ÍNDICES DE RENDIMIENTO
CREATE INDEX idx_clientes_telefono ON Clientes(telefono);
CREATE INDEX idx_pedidos_cisterna ON Pedidos(id_cisterna);
CREATE INDEX idx_pedidos_estado ON Pedidos(estado);
CREATE INDEX idx_combustible_cisterna ON RegistrosCombustible(id_cisterna);

-- DATOS INICIALES (SEED DATA)
INSERT INTO Cisternas (placa, chofer, modelo_vehiculo, rendimiento_km_galon, capacidad_total_litros, litros_asignados, litros_restantes, estado_ruta, sector_actual, latitud_actual, longitud_actual, km_odometro, km_recorridos_hoy, km_ultimo_mantenimiento, calidad_cloro_ppm, calidad_ph, activo)
VALUES 
('W4T-892', 'Carlos Mendoza', 'Volkswagen 13.180 Cabeza Ancha (Diésel)', 13.50, 10000, 6000, 4000, 'En Ruta', 'Coop. Universal', -12.044200, -76.971500, 142100.0, 18.4, 140000.0, 0.85, 7.20, TRUE),
('B7K-915', 'Manuel Quispe', 'Volkswagen Worker 15.180 Cabeza Ancha', 14.00, 10000, 10000, 0, 'Descargando', 'Asoc. Viv. Huáscar', -12.039800, -76.965200, 118350.0, 24.1, 115000.0, 0.90, 7.30, TRUE),
('F3M-104', 'Jorge Barreto', 'Volkswagen 13.180 Cabeza Ancha (Diésel)', 13.80, 10000, 0, 10000, 'En Base', 'Base Santa Anita (Av. Huarochirí)', -12.048100, -76.960200, 165800.0, 5.2, 165000.0, 0.80, 7.15, TRUE);

INSERT INTO Clientes (nombre, telefono, dni_ruc, distrito, sector, manzana_lote, direccion_referencia, latitud, longitud, plus_code, token_acceso, saldo_deuda, capacidad_tanque_litros, suscripcion_activa, dias_suscripcion, notas, activo)
VALUES 
('Rosa Huamán Soto', '998877665', '41235678', 'Santa Anita', 'Coop. Universal', 'Mz. D Lte. 14', 'Frente al parque Los Sauces, casa azul con rejas negras', -12.044500, -76.972100, '76X2724H+5V', 'tkn_cli_001_rosa', 0.00, 2000, TRUE, 'Lunes y Jueves (2,000 L)', 'Acceso con manguera de 30 metros', TRUE),
('Taller Mecánico El Chino', '987654321', '20601234567', 'Santa Anita', 'Zona Industrial Santa Anita', 'Av. De la Cultura 420', 'Portón gris frente a distribuidora', -12.046000, -76.968000, '76X2723H+9X', 'tkn_cli_002_taller', 0.00, 10000, FALSE, NULL, 'Cisterna completa requerida para lavado', TRUE),
('Comedor Popular Santa Rosa', '945612378', '10456123781', 'Santa Anita', 'Asoc. Viv. Huáscar', 'Mz. K Lte. 2', 'Al costado de la losa deportiva', -12.039200, -76.964800, '76X2726P+3C', 'tkn_cli_003_comedor', 0.00, 2000, TRUE, 'Martes y Sábados (2,000 L)', 'Recarga en tanque elevado de polietileno', TRUE);

INSERT INTO Pedidos (id_cliente, id_cisterna, modalidad, litros_agua, fecha_pedido, estado, total_soles, metodo_pago, monto_pagado, comprobante_tipo, comprobante_numero, comision_chofer, notas_entrega)
VALUES 
(1, 1, 'Fraccionado', 2000, NOW() - INTERVAL '45 minutes', 'En camino', 60.00, 'Yape', 60.00, 'Boleta', 'B001-000240', 15.00, 'Manguera tendida hacia el patio interno'),
(3, 2, 'Fraccionado', 2000, NOW() - INTERVAL '20 minutes', 'Llegando', 60.00, 'Efectivo', 0.00, 'Boleta', 'B001-000241', 15.00, 'Pago en efectivo contraentrega'),
(2, 3, 'Cisterna Completa', 10000, NOW() - INTERVAL '2 hours', 'Pendiente', 250.00, 'Credito', 0.00, 'Factura', 'F001-000085', 40.00, 'Despacho programado turno tarde');

INSERT INTO RegistrosCombustible (id_cisterna, fecha, tipo, km_odometro, km_gps_recorridos, galones_cargados, galones_estimados_gps, precio_galon, costo_total_soles, grifo, alerta_desvio, observaciones)
VALUES 
(1, NOW() - INTERVAL '1 day', 'Recarga Grifo', 142080.0, 48.6, 3.8, 3.6, 16.50, 62.70, 'Primax Santa Anita (Ovalo)', FALSE, 'Consumo dentro de parámetros normales'),
(2, NOW() - INTERVAL '2 days', 'Recarga Grifo', 118320.0, 72.0, 6.2, 5.1, 16.50, 102.30, 'Repsol Separadora Industrial', TRUE, 'Desvío de 1.1 galones por tráfico pesado en subida Huáscar');

INSERT INTO MantenimientosVehiculo (id_cisterna, fecha, tipo, km_servicio, proximo_km, costo_soles, taller, estado)
VALUES 
(1, NOW() - INTERVAL '15 days', 'Cambio de Aceite 15W40 y Filtros Diésel', 140000.0, 145000.0, 480.00, 'Taller Camiones Santa Anita', 'Al día'),
(2, NOW() - INTERVAL '28 days', 'Revisión Sistema de Frenos y Bomba de Descarga', 115000.0, 120000.0, 650.00, 'Taller Especializado Volkswagen', 'Al día');
