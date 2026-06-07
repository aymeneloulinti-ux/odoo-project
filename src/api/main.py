from __future__ import annotations

import os
import sys

# ensure src is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
# ensure the association table is imported before ORM models are used
from models import role_permission_table
from api.products import router as products_router
from api.categories import router as categories_router
from api.auth import router as auth_router
from api.roles import router as roles_router
from api.permissions import router as permissions_router
from api.warehouses import router as warehouses_router
from api.stock_movements import router as stock_movements_router
from api.users import router as users_router

app = FastAPI(title="Mini ERP API")

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(warehouses_router)
app.include_router(stock_movements_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "Mini ERP API"}


# To run locally:
# uvicorn src.api.main:app --reload
