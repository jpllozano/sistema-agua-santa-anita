-- ============================================================================
-- BASE DE DATOS: AguaSantaAnitaDB (Versión 3.0 - 100% Agua Potable en Cisternas)
-- SISTEMA DE GESTIÓN DE CISTERNAS, DESPACHO FRACCIONADO Y CONTROL DE FLOTA
-- Compatible con: Microsoft SQL Server 2017+ / Azure SQL / SQL Server Express
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AguaSantaAnitaDB')
BEGIN
    CREATE DATABASE AguaSantaAnitaDB;
END
GO

USE AguaSantaAnitaDB;
GO

-- 1. TABLA: Cisternas (Flota Volkswagen 13.180 Cabeza Ancha)
IF OBJECT_ID('dbo.MantenimientosVehiculo', 'U') IS NOT NULL DROP TABLE dbo.MantenimientosVehiculo;
IF OBJECT_ID('dbo.RegistrosCombustible', 'U') IS NOT NULL DROP TABLE dbo.RegistrosCombustible;
IF OBJECT_ID('dbo.Pedidos', 'U') IS NOT NULL DROP TABLE dbo.Pedidos;
IF OBJECT_ID('dbo.Clientes', 'U') IS NOT NULL DROP TABLE dbo.Clientes;
IF OBJECT_ID('dbo.Cisternas', 'U') IS NOT NULL DROP TABLE dbo.Cisternas;

CREATE TABLE dbo.Cisternas (
    id_cisterna INT IDENTITY(1,1) PRIMARY KEY,
    placa NVARCHAR(20) UNIQUE NOT NULL,
    chofer NVARCHAR(100) NOT NULL,
    modelo_vehiculo NVARCHAR(100) DEFAULT 'Volkswagen 13.180 Cabeza Ancha (Diésel)',
    rendimiento_km_galon DECIMAL(5, 2) DEFAULT 14.00, -- Rendimiento nominal en km/galón
    capacidad_total_litros INT DEFAULT 10000,         -- Capacidad tanque: 10,000 Litros
    litros_asignados INT DEFAULT 0,
    litros_restantes INT DEFAULT 10000,
    estado_ruta NVARCHAR(30) DEFAULT 'En Base',       -- 'En Base', 'En Ruta', 'Descargando'
    sector_actual NVARCHAR(100) DEFAULT 'Santa Anita',
    latitud_actual DECIMAL(10, 8) DEFAULT -12.043500,
    longitud_actual DECIMAL(11, 8) DEFAULT -76.969800,
    km_odometro DECIMAL(10, 1) DEFAULT 125400.0,
    km_recorridos_hoy DECIMAL(8, 2) DEFAULT 0.00,
    km_ultimo_mantenimiento DECIMAL(10, 1) DEFAULT 122000.0,
    calidad_cloro_ppm DECIMAL(4, 2) DEFAULT 0.85,     -- Cloro libre residual (0.5 - 1.0 ppm)
    calidad_ph DECIMAL(4, 2) DEFAULT 7.20,
    activo BIT DEFAULT 1
);
GO

-- 2. TABLA: Clientes y Vecinos de Santa Anita
CREATE TABLE dbo.Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(150) NOT NULL,
    telefono NVARCHAR(25) NOT NULL UNIQUE,       -- Llave única de acceso / WhatsApp
    dni_ruc NVARCHAR(20) NULL,                   -- DNI o RUC para Factura/Boleta
    distrito NVARCHAR(100) DEFAULT 'Santa Anita',
    sector NVARCHAR(100) NOT NULL,              -- Coop. Universal, Huáscar, Nocheto, etc.
    manzana_lote NVARCHAR(50) NULL,
    direccion_referencia NVARCHAR(300) NOT NULL, -- Puntos de referencia visual para chofer
    latitud DECIMAL(10, 8) NULL,
    longitud DECIMAL(11, 8) NULL,
    plus_code NVARCHAR(50) NULL,
    token_acceso NVARCHAR(64) UNIQUE NOT NULL,  -- Magic Link para autoservicio
    saldo_deuda DECIMAL(10, 2) DEFAULT 0.00,
    capacidad_tanque_litros INT DEFAULT 2000,
    suscripcion_activa BIT DEFAULT 0,
    dias_suscripcion NVARCHAR(100) NULL,        -- 'Lunes y Jueves (2,000 L)'
    notas NVARCHAR(500) NULL,
    activo BIT DEFAULT 1,
    fecha_registro DATETIME DEFAULT GETDATE()
);
GO

-- 3. TABLA: Pedidos de Agua (Despacho Fraccionado o Cisterna Completa)
CREATE TABLE dbo.Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL FOREIGN KEY REFERENCES dbo.Clientes(id_cliente),
    id_cisterna INT NULL FOREIGN KEY REFERENCES dbo.Cisternas(id_cisterna),
    modalidad NVARCHAR(30) DEFAULT 'Fraccionado', -- 'Cisterna Completa' (10,000L) o 'Fraccionado' (2,000L)
    litros_agua INT NOT NULL DEFAULT 2000,
    fecha_pedido DATETIME DEFAULT GETDATE(),
    estado NVARCHAR(30) DEFAULT 'Pendiente',      -- 'Pendiente', 'En camino', 'Llegando', 'Entregado'
    total_soles DECIMAL(10, 2) NOT NULL,
    metodo_pago NVARCHAR(30) DEFAULT 'Efectivo',  -- 'Efectivo', 'Yape', 'Plin', 'Credito'
    monto_pagado DECIMAL(10, 2) DEFAULT 0.00,
    comprobante_tipo NVARCHAR(20) DEFAULT 'Boleta', -- 'Boleta', 'Factura'
    comprobante_numero NVARCHAR(30) NULL,         -- B001-000101
    comision_chofer DECIMAL(10, 2) DEFAULT 15.00,
    notas_entrega NVARCHAR(300) NULL,
    fecha_entrega DATETIME NULL
);
GO

-- 4. TABLA: Control de Combustible (Diésel por GPS y Grifo)
CREATE TABLE dbo.RegistrosCombustible (
    id_registro INT IDENTITY(1,1) PRIMARY KEY,
    id_cisterna INT NOT NULL FOREIGN KEY REFERENCES dbo.Cisternas(id_cisterna),
    fecha DATETIME DEFAULT GETDATE(),
    tipo NVARCHAR(30) DEFAULT 'Recarga Grifo',
    km_odometro DECIMAL(10, 1) NULL,
    km_gps_recorridos DECIMAL(8, 2) DEFAULT 0.00,
    galones_cargados DECIMAL(6, 2) NOT NULL,
    galones_estimados_gps DECIMAL(6, 2) DEFAULT 0.00,
    precio_galon DECIMAL(6, 2) DEFAULT 16.50,
    costo_total_soles DECIMAL(10, 2) NOT NULL,
    grifo NVARCHAR(100) DEFAULT 'Primax Santa Anita',
    alerta_desvio BIT DEFAULT 0,
    observaciones NVARCHAR(300) NULL
);
GO

-- 5. TABLA: Mantenimiento Preventivo de Flota
CREATE TABLE dbo.MantenimientosVehiculo (
    id_mantenimiento INT IDENTITY(1,1) PRIMARY KEY,
    id_cisterna INT NOT NULL FOREIGN KEY REFERENCES dbo.Cisternas(id_cisterna),
    fecha DATETIME DEFAULT GETDATE(),
    tipo NVARCHAR(100) NOT NULL,
    km_servicio DECIMAL(10, 1) NOT NULL,
    proximo_km DECIMAL(10, 1) NOT NULL,
    costo_soles DECIMAL(10, 2) DEFAULT 0.00,
    taller NVARCHAR(100) DEFAULT 'Taller Camiones Santa Anita',
    estado NVARCHAR(20) DEFAULT 'Al día'
);
GO

-- ÍNDICES DE RENDIMIENTO
CREATE INDEX IX_Clientes_Telefono ON dbo.Clientes(telefono);
CREATE INDEX IX_Pedidos_Cisterna ON dbo.Pedidos(id_cisterna);
CREATE INDEX IX_Pedidos_Estado ON dbo.Pedidos(estado);
CREATE INDEX IX_Combustible_Cisterna ON dbo.RegistrosCombustible(id_cisterna);
GO

-- DATOS INICIALES (SEED DATA)
INSERT INTO dbo.Cisternas (placa, chofer, modelo_vehiculo, rendimiento_km_galon, capacidad_total_litros, litros_asignados, litros_restantes, estado_ruta, sector_actual, latitud_actual, longitud_actual, km_odometro, km_recorridos_hoy, km_ultimo_mantenimiento, calidad_cloro_ppm, calidad_ph, activo)
VALUES 
('W4T-892', 'Carlos Mendoza', 'Volkswagen 13.180 Cabeza Ancha (Diésel)', 13.50, 10000, 6000, 4000, 'En Ruta', 'Coop. Universal', -12.044200, -76.971500, 142100.0, 18.4, 140000.0, 0.85, 7.20, 1),
('B7K-915', 'Manuel Quispe', 'Volkswagen Worker 15.180 Cabeza Ancha', 14.00, 10000, 10000, 0, 'Descargando', 'Asoc. Viv. Huáscar', -12.039800, -76.965200, 118350.0, 24.1, 115000.0, 0.90, 7.30, 1),
('F3M-104', 'Jorge Barreto', 'Volkswagen 13.180 Cabeza Ancha (Diésel)', 13.80, 10000, 0, 10000, 'En Base', 'Base Santa Anita (Av. Huarochirí)', -12.048100, -76.960200, 165800.0, 5.2, 165000.0, 0.80, 7.15, 1);

INSERT INTO dbo.Clientes (nombre, telefono, dni_ruc, distrito, sector, manzana_lote, direccion_referencia, latitud, longitud, plus_code, token_acceso, saldo_deuda, capacidad_tanque_litros, suscripcion_activa, dias_suscripcion, notas, activo)
VALUES 
('Rosa Huamán Soto', '998877665', '41235678', 'Santa Anita', 'Coop. Universal', 'Mz. D Lte. 14', 'Frente al parque Los Sauces, casa azul con rejas negras', -12.044500, -76.972100, '76X2724H+5V', 'tkn_cli_001_rosa', 0.00, 2000, 1, 'Lunes y Jueves (2,000 L)', 'Acceso con manguera de 30 metros', 1),
('Taller Mecánico El Chino', '987654321', '20601234567', 'Santa Anita', 'Zona Industrial Santa Anita', 'Av. De la Cultura 420', 'Portón gris frente a distribuidora', -12.046000, -76.968000, '76X2723H+9X', 'tkn_cli_002_taller', 0.00, 10000, 0, NULL, 'Cisterna completa requerida para lavado', 1),
('Comedor Popular Santa Rosa', '945612378', '10456123781', 'Santa Anita', 'Asoc. Viv. Huáscar', 'Mz. K Lte. 2', 'Al costado de la losa deportiva', -12.039200, -76.964800, '76X2726P+3C', 'tkn_cli_003_comedor', 0.00, 2000, 1, 'Martes y Sábados (2,000 L)', 'Recarga en tanque elevado de polietileno', 1);

INSERT INTO dbo.Pedidos (id_cliente, id_cisterna, modalidad, litros_agua, fecha_pedido, estado, total_soles, metodo_pago, monto_pagado, comprobante_tipo, comprobante_numero, comision_chofer, notas_entrega)
VALUES 
(1, 1, 'Fraccionado', 2000, DATEADD(MINUTE, -45, GETDATE()), 'En camino', 60.00, 'Yape', 60.00, 'Boleta', 'B001-000240', 15.00, 'Manguera tendida hacia el patio interno'),
(3, 2, 'Fraccionado', 2000, DATEADD(MINUTE, -20, GETDATE()), 'Llegando', 60.00, 'Efectivo', 0.00, 'Boleta', 'B001-000241', 15.00, 'Pago en efectivo contraentrega'),
(2, 3, 'Cisterna Completa', 10000, DATEADD(HOUR, -2, GETDATE()), 'Pendiente', 250.00, 'Credito', 0.00, 'Factura', 'F001-000085', 40.00, 'Despacho programado turno tarde');

INSERT INTO dbo.RegistrosCombustible (id_cisterna, fecha, tipo, km_odometro, km_gps_recorridos, galones_cargados, galones_estimados_gps, precio_galon, costo_total_soles, grifo, alerta_desvio, observaciones)
VALUES 
(1, DATEADD(DAY, -1, GETDATE()), 'Recarga Grifo', 142080.0, 48.6, 3.8, 3.6, 16.50, 62.70, 'Primax Santa Anita (Ovalo)', 0, 'Consumo dentro de parámetros normales'),
(2, DATEADD(DAY, -2, GETDATE()), 'Recarga Grifo', 118320.0, 72.0, 6.2, 5.1, 16.50, 102.30, 'Repsol Separadora Industrial', 1, 'Desvío de 1.1 galones por tráfico pesado en subida Huáscar');

INSERT INTO dbo.MantenimientosVehiculo (id_cisterna, fecha, tipo, km_servicio, proximo_km, costo_soles, taller, estado)
VALUES 
(1, DATEADD(DAY, -15, GETDATE()), 'Cambio de Aceite 15W40 y Filtros Diésel', 140000.0, 145000.0, 480.00, 'Taller Camiones Santa Anita', 'Al día'),
(2, DATEADD(DAY, -28, GETDATE()), 'Revisión Sistema de Frenos y Bomba de Descarga', 115000.0, 120000.0, 650.00, 'Taller Especializado Volkswagen', 'Al día');
GO
