# -------------------------------------------
# back/models/places.py
# Propósito:
#   - Contratos Pydantic para "lugares" (casinos/salas).
#
# Modelos esperados:
#   1) PlaceIn (crear):
#       - name: str (obligatorio; único; aplicar .strip()).
#       - address: str | None (opcional; .strip()).
#       - is_active: bool (default True).
#     Validaciones:
#       * name no vacío; longitud razonable (ej.: 1..100) opcional.
#
#   2) PlaceUpdate (actualizar):
#       - name: str | None (misma validación si viene).
#       - address: str | None.
#       - is_active: bool | None.
#
#   3) PlaceOut (salida):
#       - id: int
#       - name: str
#       - address: str | None
#       - is_active: bool
#
# Notas:
#   - Campos de auditoría no se exponen por defecto.
#   - Borrado lógico = is_active False; no existen campos is_deleted aquí.
# -------------------------------------------

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class PlaceIn(BaseModel):
    """
    Modelo de entrada para la creación de un casino.
    Todos los campos son obligatorios.
    """
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Denominación oficial del casino"
    )
    direccion: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Ubicación física completa del establecimiento"
    )
    codigo_casino: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Identificador único del casino"
    )

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        """Valida que el nombre no esté vacío"""
        v = v.strip()
        if not v:
            raise ValueError("El nombre del casino no puede estar vacío")
        return v

    @field_validator('direccion')
    @classmethod
    def validate_direccion(cls, v: str) -> str:
        """Valida que la dirección no esté vacía"""
        v = v.strip()
        if not v:
            raise ValueError("La dirección del casino no puede estar vacía")
        return v

    @field_validator('codigo_casino')
    @classmethod
    def validate_codigo_casino(cls, v: str) -> str:
        """
        Valida el código del casino:
        - No vacío
        - Solo alfanumérico, guiones y guiones bajos
        - Convertir a mayúsculas
        """
        v = v.strip().upper()
        if not v:
            raise ValueError("El código del casino no puede estar vacío")
        
        if not all(c.isalnum() or c in ['-', '_'] for c in v):
            raise ValueError(
                "El código solo puede contener letras, números, guiones (-) y guiones bajos (_)"
            )
        
        return v


class PlaceOut(BaseModel):
    """
    Modelo de salida - lo que se retorna al crear un casino
    """
    id: int
    nombre: str
    direccion: str
    codigo_casino: str
    estado: bool = True
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class PlaceUpdate(BaseModel):
    """
    Modelo para actualizar un casino. No permite cambiar `codigo_casino`.
    """
    nombre: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Denominación oficial del casino"
    )
    direccion: Optional[str] = Field(
        None,
        min_length=10,
        max_length=200,
        description="Ubicación física completa del establecimiento"
    )
    estado: Optional[bool] = None

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("El nombre del casino no puede estar vacío")
        return v

    @field_validator('direccion')
    @classmethod
    def validate_direccion(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("La dirección del casino no puede estar vacía")
        return v
