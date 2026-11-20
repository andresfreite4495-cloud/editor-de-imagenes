"""Filtros de imagen.

Jerarquía de clases::

    Filtro (abstracta)
    ├── FiltroGrises
    ├── FiltroInvertir
    └── FiltroParametrico (abstracta)
        ├── FiltroDesenfoque
        └── FiltroContraste

Todos los filtros cumplen el mismo contrato: ``aplicar(imagen)`` recibe una
imagen de Pillow y devuelve una imagen nueva. El editor no necesita saber
qué filtro concreto está usando (polimorfismo).
"""

import math
from abc import ABC, abstractmethod

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from modelos.excepciones import ParametroInvalidoError


class Filtro(ABC):
    """Contrato común de todos los filtros (clase abstracta)."""

    def __init__(self, nombre, descripcion):
        self._nombre = nombre
        self._descripcion = descripcion

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    @abstractmethod
    def aplicar(self, imagen):
        """Devuelve una imagen nueva con el efecto aplicado.

        No debe modificar la imagen recibida.
        """

    def __str__(self):
        return f"{self._nombre}: {self._descripcion}"


class FiltroParametrico(Filtro):
    """Filtro con un valor numérico configurable dentro de un rango.

    Centraliza la validación del valor para que las clases derivadas no la
    repitan. Sigue siendo abstracta porque no implementa ``aplicar``.
    """

    def __init__(self, nombre, descripcion, etiqueta, valor, minimo, maximo):
        super().__init__(nombre, descripcion)
        self._etiqueta = etiqueta
        self._minimo = minimo
        self._maximo = maximo
        self._valor = self._validar(valor)

    @property
    def etiqueta(self):
        return self._etiqueta

    @property
    def minimo(self):
        return self._minimo

    @property
    def maximo(self):
        return self._maximo

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, nuevo_valor):
        # Solo se guarda si pasa la validación: el estado nunca queda inválido.
        self._valor = self._validar(nuevo_valor)

    def _validar(self, valor):
        if isinstance(valor, str):
            # Acepta coma decimal ("1,5"), habitual en español.
            valor = valor.strip().replace(",", ".")
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ParametroInvalidoError(
                f"{self._etiqueta} debe ser un número, no '{valor}'."
            ) from None
        if not math.isfinite(numero) or not (self._minimo <= numero <= self._maximo):
            raise ParametroInvalidoError(
                f"{self._etiqueta} debe estar entre "
                f"{self._minimo:g} y {self._maximo:g}."
            )
        return numero


class FiltroGrises(Filtro):
    def __init__(self):
        super().__init__("Escala de grises", "Convierte la imagen a tonos de gris.")

    def aplicar(self, imagen):
        return ImageOps.grayscale(imagen).convert("RGB")


class FiltroInvertir(Filtro):
    def __init__(self):
        super().__init__("Invertir colores", "Genera el negativo de la imagen.")

    def aplicar(self, imagen):
        return ImageOps.invert(imagen.convert("RGB"))


class FiltroDesenfoque(FiltroParametrico):
    def __init__(self, radio=2.0):
        super().__init__(
            "Desenfoque",
            "Suaviza la imagen con un desenfoque gaussiano.",
            "Radio",
            radio,
            0.5,
            20.0,
        )

    def aplicar(self, imagen):
        return imagen.filter(ImageFilter.GaussianBlur(self.valor))


class FiltroContraste(FiltroParametrico):
    def __init__(self, factor=1.5):
        super().__init__(
            "Contraste",
            "Aumenta (>1) o reduce (<1) la diferencia entre claros y oscuros.",
            "Factor",
            factor,
            0.2,
            3.0,
        )

    def aplicar(self, imagen):
        return ImageEnhance.Contrast(imagen).enhance(self.valor)
