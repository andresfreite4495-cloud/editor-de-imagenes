"""Pruebas de los filtros (modelos)."""

import pytest
from PIL import Image

from modelos import (
    Filtro,
    FiltroContraste,
    FiltroDesenfoque,
    FiltroGrises,
    FiltroInvertir,
    FiltroParametrico,
    ParametroInvalidoError,
)


@pytest.fixture
def imagen_color():
    return Image.new("RGB", (20, 10), (200, 40, 40))


def test_filtro_es_abstracto():
    with pytest.raises(TypeError):
        Filtro("x", "y")
    with pytest.raises(TypeError):
        FiltroParametrico("x", "y", "Valor", 1, 0, 2)


def test_grises_deja_canales_iguales(imagen_color):
    resultado = FiltroGrises().aplicar(imagen_color)
    r, g, b = resultado.getpixel((0, 0))
    assert r == g == b


def test_invertir_calcula_el_negativo(imagen_color):
    resultado = FiltroInvertir().aplicar(imagen_color)
    assert resultado.getpixel((0, 0)) == (55, 215, 215)


def test_polimorfismo_todos_los_filtros_respetan_el_contrato(imagen_color):
    filtros = [FiltroGrises(), FiltroInvertir(), FiltroDesenfoque(), FiltroContraste()]
    for filtro in filtros:
        resultado = filtro.aplicar(imagen_color)
        assert isinstance(resultado, Image.Image)
        assert resultado.size == imagen_color.size


def test_filtro_no_modifica_la_imagen_original(imagen_color):
    FiltroInvertir().aplicar(imagen_color)
    assert imagen_color.getpixel((0, 0)) == (200, 40, 40)


@pytest.mark.parametrize("valor", [0.0, 5, -1, "abc", "", None, float("nan")])
def test_contraste_rechaza_valores_invalidos(valor):
    filtro = FiltroContraste()
    with pytest.raises(ParametroInvalidoError):
        filtro.valor = valor
    assert filtro.valor == 1.5  # el estado no cambia si el valor es inválido


def test_acepta_coma_decimal():
    filtro = FiltroContraste()
    filtro.valor = "2,5"
    assert filtro.valor == 2.5


def test_desenfoque_valida_en_el_constructor():
    with pytest.raises(ParametroInvalidoError):
        FiltroDesenfoque(radio=100)
