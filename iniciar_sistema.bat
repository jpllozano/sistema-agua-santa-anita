@echo off
title Gas Santa Anita - Servidor de Reparto y Rutas
echo ============================================================
echo   SISTEMA DE GESTION DE PEDIDOS Y RUTAS - SANTA ANITA
echo ============================================================
echo.
echo Iniciando backend en Python (FastAPI + SQLite / SQL Server)...
cd backend
start "" "http://localhost:8000"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
