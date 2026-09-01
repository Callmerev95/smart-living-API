"""Agregator semua route versi v1.

Router ini di-include di `main.py` dengan prefix `/api/v1`.
Setiap modul route hanya mendaftarkan endpoint — tanpa business logic.
"""

from fastapi import APIRouter

api_v1_router = APIRouter()
