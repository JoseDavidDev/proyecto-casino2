# -------------------------------------------
# back/api/v1/places.py
# Propósito:
#   Endpoints para gestionar "lugares" (casinos/salas) en CSV.
#
# Router esperado:
#   - Variable "router" = APIRouter()
#
# Modelos (importar de back/models/places.py):
#   - PlaceIn: name, address, is_active (por defecto true).
#   - PlaceOut: id, name, address, is_active.
#
# Dependencias:
#   - get_repos() para acceder a places_repo.
#   - pagination_params(), filter_active_param() (opcional).
#
# Endpoints (sugeridos):
#   1) GET /
#      - Query: limit (int), offset (int), only_active (bool=true).
#      - Procesamiento: listar lugares, filtrar activos, paginar.
#      - Salida (200): lista PlaceOut.
#
#   2) GET /{place_id}
#      - Path: place_id (int).
#      - Procesamiento: obtener lugar por id o 404.
#      - Salida (200): PlaceOut.
#
#   3) POST /
#      - Body: PlaceIn.
#      - Validaciones:
#         * name no repetido.
#      - Procesamiento: asignar id, guardar.
#      - Salida (201): PlaceOut.
#      - Errores: 400 si nombre duplicado.
#
#   4) PUT /{place_id}
#      - Body: campos editables (name, address, is_active).
#      - Validaciones: que place_id exista; no duplicar name.
#      - Procesamiento: actualizar fila.
#      - Salida (200): PlaceOut actualizado.
#      - Errores: 404/400.
#
#   5) DELETE /{place_id}
#      - Borrado lógico:
#         * Política del proyecto: en places NO hay is_deleted, solo is_active.
#         * "Eliminar" = is_active=false (no borrar la fila).
#      - Validaciones: place_id existente.
#      - Procesamiento: marcar is_active=false.
#      - Salida (200): {"deleted": true, "id": <place_id>}
#
# Reglas adicionales:
#   - Si un lugar se desactiva (is_active=false), considerar (a nivel de dominio)
#     bloquear creación de nuevas máquinas asociadas (machines.place_id).
#     Esta comprobación NO va aquí; va en la capa domain/ o en repos.
#
# Librerías:
#   - fastapi (APIRouter, HTTPException, status)
#   - pydantic (modelos)
# -------------------------------------------

from fastapi import APIRouter, HTTPException
from back.domain.places.create import PlaceDomain
from back.models.places import PlaceIn, PlaceOut, PlaceUpdate
from back.domain.places.update import actualizar_casino


router = APIRouter()


# LISTAR / BUSCAR CASINOS
@router.get("/casino", response_model=list[PlaceOut])
def listar_casinos(consulta: str | None = None, solo_activos: bool = True, limite: int = 50, desplazamiento: int = 0):
    """
    Lista casinos con opciones de búsqueda y filtrado.

    Query params:
      - q: texto libre para buscar en nombre, dirección o código
      - only_active: si True, devuelve solo activos (por defecto True)
      - limit, offset: paginación (limit máximo 100)
    """
    # Validaciones básicas
    try:
        if limite is None:
            limite = 50
        limite = int(limite)
        desplazamiento = int(desplazamiento)
    except Exception:
        raise HTTPException(status_code=400, detail="Parámetros de paginación inválidos")

    if limite < 0 or desplazamiento < 0:
        raise HTTPException(status_code=400, detail="limite y desplazamiento deben ser >= 0")

    if limite > 100:
        limite = 100

    try:
        from back.storage.places_repo import PlaceStorage

        # Si hay texto de búsqueda, obtener todos los registros (según solo_activos) y filtrar en memoria
        if consulta:
            registros = PlaceStorage.listar(solo_activos=solo_activos, limite=None, desplazamiento=0, consulta=consulta)
            texto_norm = consulta.strip().lower()
            filtrados = []
            for r in registros:
                nombre = str(r.get('nombre', '')).lower()
                direccion = str(r.get('direccion', '')).lower()
                codigo = str(r.get('codigo_casino', '')).lower()
                if texto_norm in nombre or texto_norm in direccion or texto_norm in codigo:
                    filtrados.append(r)

            # aplicar paginación sobre la lista filtrada
            resultados = filtrados[desplazamiento: desplazamiento + limite]
        else:
            # sin texto, delegar en el repo (que ya soporta solo_activos/limite/desplazamiento)
            resultados = PlaceStorage.listar(solo_activos=solo_activos, limite=limite, desplazamiento=desplazamiento)

        # Convertir a modelos de salida
        return [PlaceOut(**r) for r in resultados]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# INACTIVAR CASINO
# --------------------------------------
@router.put("/casino/{casino_id}/inactivar")
def inactivar_casino(casino_id: int, actor: str = "system"):
    """
    Marca un casino como inactivo usando la capa de dominio.
    """
    try:
        PlaceDomain.inactivar_casino(casino_id, actor)
        return {
            "mensaje": "Casino inactivado correctamente",
            "id": casino_id,
            "actor": actor
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------
# Activar CASINO
# --------------------------------------
@router.put("/casino/{casino_id}/activar")
def activar_casino(casino_id: int, actor: str = "system"):
    """
    Marca un casino como activo usando la capa de storage
    """
    try:
        PlaceDomain.activar_casino(casino_id, actor)
        return {
            "mensaje": "Casino activado correctamente",
            "id": casino_id,
            "actor": actor
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ACTUALIZAR CASINO
@router.put("/casino/{casino_id}", response_model=PlaceOut)
def actualizar_casino_api(casino_id: int, cambios: PlaceUpdate, actor: str = "system"):
    """
    Actualiza campos editables del casino. `codigo_casino` no puede modificarse.
    """
    try:
        # Convertir modelo a dict ignorando campos None
        cambios_dict = {k: v for k, v in cambios.model_dump().items() if v is not None}
        updated = actualizar_casino(casino_id, cambios_dict, actor=actor)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=404, detail="Casino no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------------------
# CREAR CASINO
# --------------------------------------
@router.post("/casino", response_model=PlaceOut)
def crear_casino(place: PlaceIn, actor: str = "system"):
    """
    Crea un nuevo casino usando la capa de dominio.
    """
    try:
        created = PlaceDomain.create_place(place, created_by=actor)
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
