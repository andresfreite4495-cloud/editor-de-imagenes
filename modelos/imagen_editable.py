"""Representa la imagen que se está editando y su historial de cambios."""

import os

from PIL import Image, ImageOps

from modelos.excepciones import (
    ArchivoInvalidoError,
    HistorialVacioError,
    ParametroInvalidoError,
)


def _a_rgb(imagen):
    """Convierte a RGB (siempre devuelve una copia).

    Si la imagen tiene transparencia, la compone sobre fondo blanco. Así se
    evita el fondo negro y los errores al guardar como JPG.
    """
    if imagen.mode in ("RGBA", "LA") or (
        imagen.mode == "P" and "transparency" in imagen.info
    ):
        rgba = imagen.convert("RGBA")
        fondo = Image.new("RGB", rgba.size, (255, 255, 255))
        fondo.paste(rgba, mask=rgba.getchannel("A"))
        return fondo
    return imagen.convert("RGB")


class ImagenEditable:
    """Imagen actual + historial para deshacer.

    El estado (imagen actual e historial) es privado: solo se modifica a
    través de ``reemplazar`` y ``deshacer``, y ``obtener_copia`` entrega
    copias para que nadie altere la imagen por fuera.
    """

    MAX_HISTORIAL = 10
    FORMATOS_GUARDADO = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".bmp": "BMP",
    }

    def __init__(self, imagen, ruta_origen=None):
        if not isinstance(imagen, Image.Image):
            raise ParametroInvalidoError("Se esperaba una imagen de Pillow.")
        self._actual = _a_rgb(imagen)
        self._historial = []
        self._ruta_origen = ruta_origen

    @classmethod
    def desde_archivo(cls, ruta):
        """Abre un archivo de imagen o lanza ``ArchivoInvalidoError``."""
        try:
            ruta = os.fspath(ruta)
        except TypeError:
            raise ArchivoInvalidoError("La ruta del archivo no es válida.") from None
        if not os.path.isfile(ruta):
            raise ArchivoInvalidoError(f"No se encontró el archivo: {ruta}")
        try:
            with Image.open(ruta) as original:
                # Respeta la orientación EXIF (fotos tomadas con el celular).
                imagen = ImageOps.exif_transpose(original)
                imagen.load()
        except (OSError, Image.DecompressionBombError):
            raise ArchivoInvalidoError(
                "El archivo seleccionado no es una imagen válida."
            ) from None
        return cls(imagen, ruta_origen=ruta)

    # ----- consulta -----------------------------------------------------
    @property
    def ruta_origen(self):
        return self._ruta_origen

    @property
    def nombre_archivo(self):
        if self._ruta_origen:
            return os.path.basename(self._ruta_origen)
        return "sin nombre"

    @property
    def tamano(self):
        """Tupla (ancho, alto) en píxeles."""
        return self._actual.size

    @property
    def puede_deshacer(self):
        return len(self._historial) > 0

    def obtener_copia(self):
        """Devuelve una copia de la imagen actual."""
        return self._actual.copy()

    # ----- modificación -------------------------------------------------
    def reemplazar(self, nueva):
        """Guarda la imagen actual en el historial y adopta la nueva."""
        if not isinstance(nueva, Image.Image):
            raise ParametroInvalidoError("Se esperaba una imagen de Pillow.")
        nueva_rgb = _a_rgb(nueva)  # convertir primero: si falla, nada cambia
        self._historial.append(self._actual)
        if len(self._historial) > self.MAX_HISTORIAL:
            self._historial.pop(0)
        self._actual = nueva_rgb

    def deshacer(self):
        if not self._historial:
            raise HistorialVacioError()
        self._actual = self._historial.pop()

    def guardar(self, ruta):
        """Guarda la imagen actual. El formato se deduce de la extensión."""
        try:
            ruta = os.fspath(ruta)
        except TypeError:
            raise ArchivoInvalidoError("La ruta de destino no es válida.") from None
        extension = os.path.splitext(ruta)[1].lower()
        formato = self.FORMATOS_GUARDADO.get(extension)
        if formato is None:
            raise ArchivoInvalidoError(
                f"Formato '{extension or 'sin extensión'}' no soportado. "
                "Usa .png, .jpg, .jpeg o .bmp."
            )
        carpeta = os.path.dirname(ruta) or "."
        if not os.path.isdir(carpeta):
            raise ArchivoInvalidoError("La carpeta de destino no existe.")
        try:
            if formato == "JPEG":
                self._actual.save(ruta, formato, quality=95)
            else:
                self._actual.save(ruta, formato)
        except OSError as error:
            raise ArchivoInvalidoError(f"No se pudo guardar el archivo: {error}") from error
