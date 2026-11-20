# Sistema de Abastecimiento de Agua Potable en Cisternas - Santa Anita 💧🚚

Plataforma web y móvil para empresas de distribución de **agua potable en cisternas de 10,000 Litros** en Santa Anita (Coop. Universal, Huáscar, Nocheto, Los Ficus, La Encalada), con control de flota para camiones antiguos (Volkswagen cabeza ancha), despacho fraccionado, facturación electrónica SUNAT y portal de vecinos.

---

## 🚀 Novedades de la Versión 3.0 (100% Agua Potable)

### 🏢 1. Vista Empresa (Despacho & Operaciones)
* **💧 Despacho Fraccionado (10,000 L):**
  * Agrupa automáticamente hasta 5 pedidos residenciales de 2,000 Litros en un solo viaje.
  * Soporte para Cisterna Completa (10,000 L a empresas/lavanderías).
  * Barra de capacidad visual en tiempo real.
* **⛽ Control de Combustible para Camiones Mecánicos (Volkswagen Cabeza Ancha):**
  * Suma los kilómetros reales recorridos mediante GPS (fórmula de Haversine).
  * Calcula el consumo de diésel con rendimiento nominal (14 km/galón).
  * Compara los galones cargados en grifo vs los calculados por GPS y alerta si hay desvíos o fugas (>20%).
* **🧾 Facturación Electrónica SUNAT:**
  * Emisión automática de **Boletas (Serie B001)** y **Facturas (Serie F001)** con DNI o RUC.
  * Modal con vista de **Ticket Térmico Imprimible**.
* **🔧 Mantenimiento Preventivo de Flota:**
  * Control de odómetro: alertas para cambio de aceite 15W40 cada 5,000 km, engrase de válvulas y bomba de agua.
* **👨‍✈️ Liquidación de Choferes:**
  * Registro de comisiones por viaje entregado (S/ 15 por fraccionado, S/ 30 por cisterna completa).

---

### 👤 2. Vista Cliente (Portal del Vecino)
* **Acceso Directo con Celular:** Cero contraseñas o registros obligatorios.
* **Mapa de Cisterna en Vivo:** Muestra el camión acercándose a su calle o escalera en Santa Anita.
* **🧪 Sello de Calidad del Agua:** Muestra los niveles de cloro residual (0.85 ppm) y pH (7.2) garantizando agua 100% apta para consumo humano según normativa.
* **📅 Recarga Periódica Automática:** Suscripción programada (ej: "Lunes y Jueves - 2,000 L").
* **💬 Contacto Directo:** Enlace rápido de WhatsApp para pedir recargas en 1 toque.

---

## 📁 Archivos del Proyecto
* [iniciar_sistema.bat](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/iniciar_sistema.bat) - Lanzador con un solo clic.
* [backend/main.py](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/backend/main.py) - API FastAPI con endpoints de agua, combustible y facturación.
* [backend/models.py](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/backend/models.py) - Modelos SQLAlchemy (Cisternas, Combustible, Mantenimiento, Clientes, Pedidos).
* [backend/crud.py](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/backend/crud.py) - Lógica de despacho fraccionado, Haversine GPS y detección de desvíos.
* [frontend/index.html](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/frontend/index.html) - Aplicación React con interfaz dual, mapas OpenStreetMap y ticket SUNAT.
* [database/schema_sqlserver.sql](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/database/schema_sqlserver.sql) - Script completo T-SQL para Microsoft SQL Server.

---

## 🏃‍♂️ Cómo Ejecutar
1. Haz doble clic en [`iniciar_sistema.bat`](file:///c:/Users/Administrador/Desktop/Proyectos_Personales/gas-delivery-santa-anita/iniciar_sistema.bat).
2. Abre tu navegador en: **[http://localhost:8000](http://localhost:8000)**.
