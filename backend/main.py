import os
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, Base, get_db
import models
import schemas
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Abastecimiento de Agua Potable en Cisternas - Santa Anita",
    description="Plataforma de Doble Vista: Gestión de Flota Volkswagen, Control de Combustible GPS/Odómetro, Despacho Fraccionado (10,000L), Mantenimiento Preventivo y Portal del Vecino.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        crud.seed_initial_data(db)
    finally:
        db.close()

# ----------------- PORTAL DEL CLIENTE (SIN CONTRASEÑA) -----------------

@app.get("/api/seguimiento/{identificador}", response_model=schemas.SeguimientoCliente)
def seguimiento_cliente(identificador: str, db: Session = Depends(get_db)):
    data = crud.get_seguimiento_cliente(db, identificador)
    if not data:
        raise HTTPException(status_code=404, detail="No se encontró registro para este número de teléfono")
    return data

@app.post("/api/cliente/pedido-rapido", response_model=schemas.PedidoOut)
def pedido_rapido_cliente(pedido_in: schemas.PedidoCreate, db: Session = Depends(get_db)):
    return crud.create_pedido(db, pedido_in)

# ----------------- GESTIÓN DE CISTERNAS Y DESPACHO -----------------

@app.get("/api/cisternas", response_model=List[schemas.CisternaOut])
def list_cisternas(db: Session = Depends(get_db)):
    return crud.get_cisternas(db)

@app.get("/api/cisternas/{id_cisterna}", response_model=schemas.CisternaOut)
def read_cisterna(id_cisterna: int, db: Session = Depends(get_db)):
    c = crud.get_cisterna(db, id_cisterna)
    if not c:
        raise HTTPException(status_code=404, detail="Cisterna no encontrada")
    return c

@app.put("/api/cisternas/{id_cisterna}/ubicacion", response_model=schemas.CisternaOut)
def update_ubicacion_cisterna(
    id_cisterna: int,
    lat: float = Query(...),
    lng: float = Query(...),
    sector: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    c = crud.update_cisterna_ubicacion(db, id_cisterna, lat, lng, sector)
    if not c:
        raise HTTPException(status_code=404, detail="Cisterna no encontrada")
    return c

@app.post("/api/cisternas/asignar-ruta", response_model=schemas.CisternaOut)
def asignar_ruta(payload: schemas.AsignacionCisterna, db: Session = Depends(get_db)):
    res = crud.asignar_pedidos_a_cisterna(db, payload.id_cisterna, payload.pedidos_ids)
    if not res:
        raise HTTPException(status_code=400, detail="Error al asignar pedidos a la cisterna")
    return res

# ----------------- CONTROL DE COMBUSTIBLE Y MANTENIMIENTO -----------------

@app.post("/api/combustible/recarga", response_model=schemas.RegistroCombustibleOut)
def registrar_recarga(recarga_in: schemas.RegistroCombustibleCreate, db: Session = Depends(get_db)):
    reg = crud.registrar_combustible(db, recarga_in)
    if not reg:
        raise HTTPException(status_code=400, detail="Error al registrar combustible")
    return reg

@app.get("/api/combustible", response_model=List[schemas.RegistroCombustibleOut])
def list_combustible(id_cisterna: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_registros_combustible(db, id_cisterna=id_cisterna)

@app.get("/api/mantenimientos", response_model=List[schemas.MantenimientoOut])
def list_mantenimientos(id_cisterna: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_mantenimientos(db, id_cisterna=id_cisterna)

# ----------------- ADMINISTRACIÓN GENERAL -----------------

@app.get("/api/stats", response_model=schemas.ResumenEstadisticas)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@app.get("/api/clientes", response_model=List[schemas.ClienteOut])
def list_clientes(
    search: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_clientes(db, search=search, sector=sector)

@app.post("/api/clientes", response_model=schemas.ClienteOut)
def create_cliente(cliente_in: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return crud.create_cliente(db, cliente_in)

@app.get("/api/pedidos", response_model=List[schemas.PedidoOut])
def list_pedidos(estado: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_pedidos(db, estado=estado)

@app.post("/api/pedidos", response_model=schemas.PedidoOut)
def create_pedido(pedido_in: schemas.PedidoCreate, db: Session = Depends(get_db)):
    return crud.create_pedido(db, pedido_in)

@app.put("/api/pedidos/{id_pedido}/status", response_model=schemas.PedidoOut)
def update_pedido_status(
    id_pedido: int,
    status_in: schemas.PedidoStatusUpdate,
    db: Session = Depends(get_db)
):
    p = crud.update_pedido_status(db, id_pedido, status_in)
    if not p:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return p

# Servir Frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend en desarrollo"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
