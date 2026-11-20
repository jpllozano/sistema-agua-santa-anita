-- ============================================================================
-- BASE DE DATOS: AguaSantaAnitaDB (Versión 3.0 - 100% Agua Potable)
-- SISTEMA DE GESTIÓN DE CISTERNAS, DESPACHO FRACCIONADO Y CONTROL DE FLOTA
-- Compatible con: Microsoft SQL Server 2017+ / Azure SQL
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AguaSantaAnitaDB')
BEGIN
    CREATE DATABASE AguaSantaAnitaDB;
END
GO

USE AguaSantaAnitaDB;
GO

-- 1. TABLA: Cisternas (Flota Volkswagen Cabeza Ancha)
IF OBJECT_ID('dbo.Cisternas', 'U') IS NOT NULL DROP TABLE dbo.Cisternas;
CREATE TABLE dbo.Cisternas (
    id_cisterna INT IDENTITY(1,1) PRIMARY KEY,
    placa NVARCHAR(20) UNIQUE NOT NULL,
    chofer NVARCHAR(100) NOT NULL,
    modelo_vehiculo NVARCHAR(100) DEFAULT 'Volkswagen 13.180 Cabeza Ancha (Diésel)',
    rendimiento_km_galon DECIMAL(5, 2) DEFAULT 14.00, -- Rendimiento nominal
    capacidad_total_litros INT DEFAULT 10000,         -- 10,000 Litros
    litros_asignados INT DEFAULT 0,
    litros_restantes INT DEFAULT 10000,
    estado_ruta NVARCHAR(30) DEFAULT 'En Base',       -- 'En Base', 'En Ruta', 'Descargando'
    sector_actual NVARCHAR(100) DEFAULT 'Santa Anita',
    latitud_actual DECIMAL(10, 8) DEFAULT -12.043500,
    longitud_actual DECIMAL(11, 8) DEFAULT -76.969800,
    km_odometro DECIMAL(10, 1) DEFAULT 125400.0,
    km_recorridos_hoy DECIMAL(8, 2) DEFAULT 0.00,
    km_ultimo_mantenimiento DECIMAL(10, 1) DEFAULT 122000.0,
    calidad_cloro_ppm DECIMAL(4, 2) DEFAULT 0.85,     -- Cloro residual (0.5 a 1.0 ppm)
    calidad_ph DECIMAL(4, 2) DEFAULT 7.20,
    activo BIT DEFAULT 1
);
GO

-- 2. TABLA: Clientes y Vecinos de Santa Anita
IF OBJECT_ID('dbo.Clientes', 'U') IS NOT NULL DROP TABLE dbo.Clientes;
CREATE TABLE dbo.Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(150) NOT NULL,
    telefono NVARCHAR(25) NOT NULL UNIQUE,       -- Llave única de acceso del cliente
    dni_ruc NVARCHAR(20) NULL,                   -- DNI o RUC para Factura/Boleta
    distrito NVARCHAR(100) DEFAULT 'Santa Anita',
    sector NVARCHAR(100) NOT NULL,              -- Coop. Universal, Huáscar, Nocheto, etc.
    manzana_lote NVARCHAR(50) NULL,
    direccion_referencia NVARCHAR(300) NOT NULL, -- Puntos de referencia visual
    latitud DECIMAL(10, 8) NULL,
    longitud DECIMAL(11, 8) NULL,
    plus_code NVARCHAR(50) NULL,
    token_acceso NVARCHAR(64) UNIQUE NOT NULL,  -- Magic Link para WhatsApp
    saldo_deuda DECIMAL(10, 2) DEFAULT 0.00,
    capacidad_tanque_litros INT DEFAULT 2000,
    suscripcion_activa BIT DEFAULT 0,
    dias_suscripcion NVARCHAR(100) NULL,        -- 'Lunes y Jueves (2,000 L)'
    notas NVARCHAR(500) NULL,
    activo BIT DEFAULT 1,
    fecha_registro DATETIME DEFAULT GETDATE()
);
GO

-- 3. TABLA: Pedidos de Agua (Fraccionado o Cisterna Completa)
IF OBJECT_ID('dbo.Pedidos', 'U') IS NOT NULL DROP TABLE dbo.Pedidos;
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
IF OBJECT_ID('dbo.RegistrosCombustible', 'U') IS NOT NULL DROP TABLE dbo.RegistrosCombustible;
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
IF OBJECT_ID('dbo.MantenimientosVehiculo', 'U') IS NOT NULL DROP TABLE dbo.MantenimientosVehiculo;
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

-- ÍNDICES
CREATE INDEX IX_Clientes_Telefono ON dbo.Clientes(telefono);
CREATE INDEX IX_Pedidos_Cisterna ON dbo.Pedidos(id_cisterna);
CREATE INDEX IX_Pedidos_Estado ON dbo.Pedidos(estado);
CREATE INDEX IX_Combustible_Cisterna ON dbo.RegistrosCombustible(id_cisterna);
GO
