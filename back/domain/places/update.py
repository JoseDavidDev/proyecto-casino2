from back.storage.places_repo import PlaceStorage
from back.models.places import PlaceUpdate, PlaceOut


def actualizar_casino(id_lugar: int, cambios: dict, actor: str = "system") -> PlaceOut:
    """
    Lógica de dominio para actualizar un casino.

    - Verifica existencia
    - Impide la modificación de `codigo_casino`
    - Verifica duplicado de nombre
    - Aplica cambios vía repositorio y devuelve PlaceOut
    """
    # Comprobar existencia
    existente = PlaceStorage.obtener_por_id(id_lugar)
    if not existente:
        raise KeyError(f"No existe un casino con ID {id_lugar}")

    # Prohibir cambio de codigo_casino
    if 'codigo_casino' in cambios and cambios.get('codigo_casino'):
        codigo_nuevo = str(cambios.get('codigo_casino', '')).strip().upper()
        codigo_actual = str(existente.get('codigo_casino', '')).strip().upper()
        if codigo_nuevo and codigo_nuevo != codigo_actual:
            raise ValueError("El 'codigo_casino' no se puede modificar una vez creado")

    # Si cambia nombre, verificar duplicado
    if 'nombre' in cambios and cambios.get('nombre'):
        nuevo_nombre = cambios.get('nombre')
        if PlaceStorage.existe_nombre(nuevo_nombre, excluir_id=id_lugar):
            raise ValueError(f"Ya existe otro casino con el nombre '{nuevo_nombre}'")

    # Aplicar actualización en el repositorio
    actualizado = PlaceStorage.actualizar_fila(id_lugar, cambios, actor=actor)
    if not actualizado:
        raise Exception("Error al actualizar el casino")

    return PlaceOut(**actualizado)
# -------------------------------------------
# back/domain/places/update.py
# Función: actualizar_place(place_id, cambios, clock, repo, actor)
#
# Entradas:
#   - place_id: int
#   - cambios: dict (name, address, is_active)
#   - clock, repo, actor
#
# Validaciones:
#   - place existente
#   - si cambia name, no duplicar con otro registro
#
# Procesamiento:
#   - Aplicar cambios permitidos
#   - updated_at/by = clock()/actor
#   - Guardar
#
# Salida:
#   - {id, name, address, is_active}
#
# Errores:
#   - NotFoundError, ValueError (duplicado)
# -------------------------------------------
