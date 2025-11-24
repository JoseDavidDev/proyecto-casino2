# -------------------------------------------
# back/api/router.py
# Propósito:
#   - Declarar un APIRouter "raíz" e incluir los routers de cada recurso/versión.
#   - Definir prefijos, tags y versionamiento (p. ej., /api/v1).
#
# Qué debe exponer:
#   - Una variable "api_router" de tipo APIRouter que sea incluida por back/main.py.
#
# Contenido esperado:
#   - Importa APIRouter desde fastapi.
#   - Importa routers de back/api/v1 (health, users, places, machines).
#   - Crea "api_router = APIRouter()" e incluye:
#       api_router.include_router(health.router,  prefix="/v1",         tags=["health"])
#       api_router.include_router(users.router,   prefix="/v1/users",   tags=["users"])
#       api_router.include_router(places.router,  prefix="/v1/places",  tags=["places"])
#       api_router.include_router(machines.router,prefix="/v1/machines",tags=["machines"])
#       Y así sucesivamente para otros recursos.
#
# Reglas/decisiones:
#   - Mantener versionamiento en el path (ej.: /api/v1/*) para que futuras
#     versiones convivan sin romper clientes.
#   - No colocar lógica de negocio aquí, solo "enrutamiento".
# -------------------------------------------

from fastapi import APIRouter

from back.api.v1.auth import router as auth_router 
from back.api.v1.users import router as users_router
from back.api.v1.places import router as places_router

# Prefijo correcto para que Swagger lo muestre como /api/v1/...
api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router, tags=["auth"]) 
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(places_router, prefix="/places", tags=["places"])
