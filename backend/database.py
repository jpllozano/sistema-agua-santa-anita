import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de conexión
RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://localhost/AguaSantaAnitaDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Compatibilidad con PostgreSQL (Supabase / Render / Heroku):
# Si viene como postgres:// o postgresql://, aseguramos el dialecto estándar postgresql+psycopg2://
if RAW_DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif RAW_DATABASE_URL.startswith("postgresql://") and not RAW_DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = RAW_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    DATABASE_URL = RAW_DATABASE_URL

SQLITE_FALLBACK_URL = "sqlite:///./gas_delivery.db"

engine = None
SessionLocal = None
Base = declarative_base()

def init_db_engine():
    global engine, SessionLocal
    # Intentamos primero con SQL Server si está configurado
    if "mssql" in DATABASE_URL:
        try:
            test_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with test_engine.connect() as conn:
                print(" Conexión exitosa a Microsoft SQL Server (AguaSantaAnitaDB)")
            engine = test_engine
        except Exception as e:
            print(f" Aviso: No se pudo conectar a SQL Server ({e}).")
            print(" Usando base de datos SQLite local para desarrollo/pruebas continuas.")
            engine = create_engine(
                SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
    else:
        # PostgreSQL (Supabase) o SQLite
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            with engine.connect() as conn:
                print(" Conexión exitosa a la base de datos PostgreSQL")
        except Exception as e:
            print(f" Aviso al conectar a la base de datos principal ({e}). Usando fallback SQLite.")
            engine = create_engine(
                SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

init_db_engine()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
