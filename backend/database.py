import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de conexión
# Formato SQL Server para Windows con autenticación de Windows:
# mssql+pyodbc://localhost/GasDeliveryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
SQL_SERVER_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://localhost/GasDeliveryDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

SQLITE_FALLBACK_URL = "sqlite:///./gas_delivery.db"

engine = None
SessionLocal = None
Base = declarative_base()

def init_db_engine():
    global engine, SessionLocal
    # Intentamos primero con SQL Server si está configurado
    if "mssql" in SQL_SERVER_URL:
        try:
            test_engine = create_engine(SQL_SERVER_URL, pool_pre_ping=True)
            with test_engine.connect() as conn:
                print(" Conexión exitosa a Microsoft SQL Server (GasDeliveryDB)")
            engine = test_engine
        except Exception as e:
            print(f" Aviso: No se pudo conectar a SQL Server ({e}).")
            print(" Usando base de datos SQLite local para desarrollo/pruebas continuas.")
            engine = create_engine(
                SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
    else:
        engine = create_engine(SQL_SERVER_URL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

init_db_engine()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
