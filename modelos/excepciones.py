"""Excepciones propias de la aplicación.

Todas heredan de ``EditorError``. De esta forma la interfaz gráfica puede
capturar cualquier error previsible con un solo ``except EditorError`` y
mostrar un mensaje claro al usuario, sin conocer los detalles internos.
"""


class EditorError(Exception):
    """Clase base de los errores previsibles del editor."""


class ImagenNoCargadaError(EditorError):
    """Se intentó operar sin tener una imagen abierta."""

    def __init__(self, mensaje="Primero debes abrir una imagen."):
        super().__init__(mensaje)


class ArchivoInvalidoError(EditorError):
    """El archivo no existe, no es una imagen o no se pudo guardar."""


class ParametroInvalidoError(EditorError):
    """Un valor ingresado (factor, ángulo, tamaño...) no es válido."""


class HistorialVacioError(EditorError):
    """No hay cambios anteriores a los cuales volver."""

    def __init__(self, mensaje="No hay cambios para deshacer."):
        super().__init__(mensaje)
