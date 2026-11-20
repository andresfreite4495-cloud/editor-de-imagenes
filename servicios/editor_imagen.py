"""Lógica de aplicación: coordina la imagen y los filtros.

``EditorImagen`` es el único punto de entrada para la interfaz. Valida los
datos que llegan (la interfaz le pasa texto tal como lo escribió el usuario)
y lanza excepciones propias que la ventana convierte en mensajes.
"""

from PIL import Image

from modelos.excepciones import ImagenNoCargadaError, ParametroInvalidoError
from modelos.filtros import Filtro, FiltroParametrico
from modelos.imagen_editable import ImagenEditable


class EditorImagen:
    TAMANO_MAXIMO = 8000  # píxeles por lado
    ANGULOS_VALIDOS = (90, 180, 270)

    def __init__(self, filtros=()):
        # Composición: el editor crea y es dueño de su ImagenEditable
        # (nace en ``cargar`` y deja de existir si el editor desaparece).
        self._imagen = None
        # Agregación: los filtros se crean fuera y se entregan al editor;
        # existen independientemente de él.
        self._filtros = {}
        for filtro in filtros:
            self.registrar_filtro(filtro)

    # ----- filtros disponibles -----------------------------------------
    def registrar_filtro(self, filtro):
        if not isinstance(filtro, Filtro):
            raise ParametroInvalidoError("Solo se pueden registrar objetos de tipo Filtro.")
        if filtro.nombre in self._filtros:
            raise ParametroInvalidoError(f"Ya existe un filtro llamado '{filtro.nombre}'.")
        self._filtros[filtro.nombre] = filtro

    @property
    def filtros_disponibles(self):
        return list(self._filtros)

    def parametro_de(self, nombre):
        """Devuelve (etiqueta, mínimo, máximo, valor) o None si no tiene parámetro."""
        filtro = self._obtener_filtro(nombre)
        if isinstance(filtro, FiltroParametrico):
            return (filtro.etiqueta, filtro.minimo, filtro.maximo, filtro.valor)
        return None

    def _obtener_filtro(self, nombre):
        try:
            return self._filtros[nombre]
        except KeyError:
            raise ParametroInvalidoError(f"El filtro '{nombre}' no existe.") from None

    # ----- estado -------------------------------------------------------
    @property
    def hay_imagen(self):
        return self._imagen is not None

    @property
    def puede_deshacer(self):
        return self.hay_imagen and self._imagen.puede_deshacer

    @property
    def tamano(self):
        return self._imagen.tamano if self.hay_imagen else None

    @property
    def nombre_archivo(self):
        return self._imagen.nombre_archivo if self.hay_imagen else None

    def imagen_actual(self):
        """Copia de la imagen actual, lista para mostrar."""
        self._requerir_imagen()
        return self._imagen.obtener_copia()

    def _requerir_imagen(self):
        if self._imagen is None:
            raise ImagenNoCargadaError()

    # ----- operaciones --------------------------------------------------
    def cargar(self, ruta):
        # Se asigna solo si la carga tuvo éxito: un archivo inválido no
        # descarta la imagen que ya estaba abierta.
        self._imagen = ImagenEditable.desde_archivo(ruta)

    def aplicar_filtro(self, nombre, valor=None):
        self._requerir_imagen()
        filtro = self._obtener_filtro(nombre)
        if valor is not None:
            if not isinstance(filtro, FiltroParametrico):
                raise ParametroInvalidoError(f"El filtro '{nombre}' no admite parámetros.")
            filtro.valor = valor  # el setter valida el rango
        # Polimorfismo: cada filtro concreto responde distinto a aplicar().
        resultado = filtro.aplicar(self._imagen.obtener_copia())
        self._imagen.reemplazar(resultado)

    def rotar(self, grados):
        """Rota en múltiplos de 90°. Positivo = antihorario, negativo = horario."""
        self._requerir_imagen()
        try:
            angulo = int(str(grados).strip()) % 360
        except ValueError:
            raise ParametroInvalidoError("El ángulo debe ser un número entero.") from None
        if angulo not in self.ANGULOS_VALIDOS:
            raise ParametroInvalidoError("Solo se puede rotar 90°, 180° o 270°.")
        rotada = self._imagen.obtener_copia().rotate(angulo, expand=True)
        self._imagen.reemplazar(rotada)

    def redimensionar(self, ancho, alto):
        self._requerir_imagen()
        nuevo_ancho = self._entero_valido(ancho, "El ancho")
        nuevo_alto = self._entero_valido(alto, "El alto")
        nueva = self._imagen.obtener_copia().resize(
            (nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS
        )
        self._imagen.reemplazar(nueva)

    def deshacer(self):
        self._requerir_imagen()
        self._imagen.deshacer()

    def exportar(self, ruta):
        self._requerir_imagen()
        self._imagen.guardar(ruta)

    def _entero_valido(self, valor, nombre):
        try:
            numero = int(str(valor).strip())
        except ValueError:
            raise ParametroInvalidoError(f"{nombre} debe ser un número entero.") from None
        if not 1 <= numero <= self.TAMANO_MAXIMO:
            raise ParametroInvalidoError(
                f"{nombre} debe estar entre 1 y {self.TAMANO_MAXIMO} píxeles."
            )
        return numero
