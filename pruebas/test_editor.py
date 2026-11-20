"""Pruebas del editor (servicio) y de la imagen editable."""

import pytest
from PIL import Image

from modelos import (
    ArchivoInvalidoError,
    FiltroContraste,
    FiltroDesenfoque,
    FiltroGrises,
    FiltroInvertir,
    HistorialVacioError,
    ImagenEditable,
    ImagenNoCargadaError,
    ParametroInvalidoError,
)
from servicios import EditorImagen


@pytest.fixture
def ruta_imagen(tmp_path):
    ruta = tmp_path / "foto.png"
    Image.new("RGB", (40, 20), (10, 120, 200)).save(ruta)
    return str(ruta)


@pytest.fixture
def editor():
    return EditorImagen(
        [FiltroGrises(), FiltroInvertir(), FiltroDesenfoque(), FiltroContraste()]
    )


@pytest.fixture
def editor_con_imagen(editor, ruta_imagen):
    editor.cargar(ruta_imagen)
    return editor


# ---------------------------------------------------------------- cargar
def test_cargar_imagen_valida(editor, ruta_imagen):
    assert not editor.hay_imagen
    editor.cargar(ruta_imagen)
    assert editor.hay_imagen
    assert editor.tamano == (40, 20)
    assert editor.nombre_archivo == "foto.png"


def test_cargar_archivo_que_no_es_imagen(editor, tmp_path):
    falso = tmp_path / "notas.txt"
    falso.write_text("esto no es una imagen")
    with pytest.raises(ArchivoInvalidoError):
        editor.cargar(str(falso))
    assert not editor.hay_imagen


def test_cargar_archivo_inexistente(editor, tmp_path):
    with pytest.raises(ArchivoInvalidoError):
        editor.cargar(str(tmp_path / "no_existe.png"))


def test_carga_fallida_no_descarta_la_imagen_abierta(editor_con_imagen, tmp_path):
    falso = tmp_path / "notas.txt"
    falso.write_text("nada")
    with pytest.raises(ArchivoInvalidoError):
        editor_con_imagen.cargar(str(falso))
    assert editor_con_imagen.hay_imagen
    assert editor_con_imagen.tamano == (40, 20)


def test_imagen_con_transparencia_se_convierte_a_rgb(editor, tmp_path):
    ruta = tmp_path / "transparente.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 0)).save(ruta)
    editor.cargar(str(ruta))
    assert editor.imagen_actual().mode == "RGB"
    assert editor.imagen_actual().getpixel((0, 0)) == (255, 255, 255)


# ---------------------------------------------------- operaciones sin imagen
@pytest.mark.parametrize(
    "operacion",
    [
        lambda e: e.aplicar_filtro("Escala de grises"),
        lambda e: e.rotar(90),
        lambda e: e.redimensionar(10, 10),
        lambda e: e.deshacer(),
        lambda e: e.exportar("salida.png"),
        lambda e: e.imagen_actual(),
    ],
)
def test_operar_sin_imagen_lanza_error(editor, operacion):
    with pytest.raises(ImagenNoCargadaError):
        operacion(editor)


# --------------------------------------------------------------- filtros
def test_aplicar_filtro_cambia_la_imagen(editor_con_imagen):
    antes = editor_con_imagen.imagen_actual().getpixel((0, 0))
    editor_con_imagen.aplicar_filtro("Invertir colores")
    assert editor_con_imagen.imagen_actual().getpixel((0, 0)) != antes


def test_aplicar_filtro_con_parametro_valido(editor_con_imagen):
    editor_con_imagen.aplicar_filtro("Contraste", "2,0")
    assert editor_con_imagen.puede_deshacer


def test_aplicar_filtro_con_parametro_invalido(editor_con_imagen):
    with pytest.raises(ParametroInvalidoError):
        editor_con_imagen.aplicar_filtro("Contraste", "99")
    assert not editor_con_imagen.puede_deshacer  # no se aplicó nada


def test_filtro_sin_parametros_rechaza_valor(editor_con_imagen):
    with pytest.raises(ParametroInvalidoError):
        editor_con_imagen.aplicar_filtro("Escala de grises", "3")


def test_filtro_inexistente(editor_con_imagen):
    with pytest.raises(ParametroInvalidoError):
        editor_con_imagen.aplicar_filtro("Sepia")


def test_parametro_de(editor):
    assert editor.parametro_de("Escala de grises") is None
    etiqueta, minimo, maximo, valor = editor.parametro_de("Contraste")
    assert (etiqueta, minimo, maximo, valor) == ("Factor", 0.2, 3.0, 1.5)


def test_registrar_filtro_invalido_o_repetido(editor):
    with pytest.raises(ParametroInvalidoError):
        editor.registrar_filtro("no soy un filtro")
    with pytest.raises(ParametroInvalidoError):
        editor.registrar_filtro(FiltroGrises())


# ------------------------------------------------------------- transformar
def test_rotar_90_intercambia_dimensiones(editor_con_imagen):
    editor_con_imagen.rotar(90)
    assert editor_con_imagen.tamano == (20, 40)


def test_rotar_negativo_es_horario(editor_con_imagen):
    editor_con_imagen.rotar(-90)
    assert editor_con_imagen.tamano == (20, 40)


@pytest.mark.parametrize("angulo", [45, 0, 360, "abc", None, 1.5])
def test_rotar_angulo_invalido(editor_con_imagen, angulo):
    with pytest.raises(ParametroInvalidoError):
        editor_con_imagen.rotar(angulo)


def test_redimensionar_valido_con_texto(editor_con_imagen):
    editor_con_imagen.redimensionar("100", " 50 ")
    assert editor_con_imagen.tamano == (100, 50)


@pytest.mark.parametrize(
    "ancho, alto",
    [("abc", "10"), ("10", ""), ("0", "10"), ("-5", "10"), ("10.5", "10"), ("99999", "10")],
)
def test_redimensionar_entradas_invalidas(editor_con_imagen, ancho, alto):
    with pytest.raises(ParametroInvalidoError):
        editor_con_imagen.redimensionar(ancho, alto)
    assert editor_con_imagen.tamano == (40, 20)


# ---------------------------------------------------------------- deshacer
def test_deshacer_restaura_el_estado_anterior(editor_con_imagen):
    editor_con_imagen.redimensionar(10, 10)
    editor_con_imagen.rotar(90)
    editor_con_imagen.deshacer()
    assert editor_con_imagen.tamano == (10, 10)
    editor_con_imagen.deshacer()
    assert editor_con_imagen.tamano == (40, 20)
    assert not editor_con_imagen.puede_deshacer


def test_deshacer_sin_historial(editor_con_imagen):
    with pytest.raises(HistorialVacioError):
        editor_con_imagen.deshacer()


def test_historial_tiene_limite(editor_con_imagen):
    for _ in range(ImagenEditable.MAX_HISTORIAL + 5):
        editor_con_imagen.rotar(90)
    pasos = 0
    while editor_con_imagen.puede_deshacer:
        editor_con_imagen.deshacer()
        pasos += 1
    assert pasos == ImagenEditable.MAX_HISTORIAL


# ---------------------------------------------------------------- exportar
@pytest.mark.parametrize("nombre", ["salida.png", "salida.jpg", "salida.bmp"])
def test_exportar_formatos_validos(editor_con_imagen, tmp_path, nombre):
    destino = tmp_path / nombre
    editor_con_imagen.exportar(str(destino))
    with Image.open(destino) as guardada:
        assert guardada.size == (40, 20)


def test_exportar_extension_no_soportada(editor_con_imagen, tmp_path):
    with pytest.raises(ArchivoInvalidoError):
        editor_con_imagen.exportar(str(tmp_path / "salida.xyz"))
    with pytest.raises(ArchivoInvalidoError):
        editor_con_imagen.exportar(str(tmp_path / "sin_extension"))


def test_exportar_en_carpeta_inexistente(editor_con_imagen, tmp_path):
    with pytest.raises(ArchivoInvalidoError):
        editor_con_imagen.exportar(str(tmp_path / "no_existe" / "salida.png"))


# ----------------------------------------------------------- encapsulamiento
def test_imagen_actual_entrega_una_copia(editor_con_imagen):
    copia = editor_con_imagen.imagen_actual()
    copia.putpixel((0, 0), (1, 2, 3))
    assert editor_con_imagen.imagen_actual().getpixel((0, 0)) == (10, 120, 200)
