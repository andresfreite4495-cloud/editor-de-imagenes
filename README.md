# Editor de Imágenes

Aplicación de escritorio en Python para abrir una imagen, aplicarle filtros, rotarla, cambiarle el tamaño y guardar el resultado. Está construida con **programación orientada a objetos**, **Tkinter** para la interfaz gráfica y **Pillow** para el procesamiento de imágenes.

> Proyecto del parcial integrador de Programación Orientada a Objetos con Python.
> La explicación técnica del diseño está en [`docs/INFORME_TECNICO.md`](docs/INFORME_TECNICO.md).

## 1. Descripción del problema

Editar una imagen de forma básica (pasarla a blanco y negro, aumentar el contraste, girarla o reducir su tamaño) suele requerir programas pesados o complejos. Esta aplicación ofrece un editor sencillo, con una interfaz clara, que resuelve esas tareas comunes y permite deshacer los cambios.

## 2. Objetivos

- Permitir editar una imagen desde una interfaz gráfica sin conocimientos técnicos.
- Aplicar de forma real los conceptos de POO vistos en el semestre: clases, encapsulamiento, herencia, polimorfismo, abstracción y relaciones entre objetos.
- Mantener separadas la lógica, los modelos y la interfaz.
- Manejar los errores previsibles (archivos inválidos, valores fuera de rango) con mensajes claros.

## 3. Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| Abrir imagen y vista previa | Carga PNG, JPG, BMP, GIF o WEBP y la muestra ajustada a la ventana. |
| Filtros | Escala de grises, invertir colores, desenfoque (radio ajustable) y contraste (factor ajustable). |
| Rotar | Gira la imagen 90° a la izquierda o a la derecha. |
| Redimensionar | Cambia el tamaño indicando ancho y alto en píxeles. |
| Deshacer | Vuelve al estado anterior (hasta 10 pasos). |
| Guardar como | Exporta el resultado en PNG, JPG o BMP. |

Atajos de teclado: `Ctrl+O` abrir, `Ctrl+S` guardar, `Ctrl+Z` deshacer.

## 4. Tecnologías utilizadas

- **Python** (3.10 o superior)
- **Tkinter / ttk**: interfaz gráfica (incluida con Python).
- **Pillow**: lectura, procesamiento y guardado de imágenes.
- **pytest**: pruebas automatizadas (opcional, solo para desarrollo).
- **Git y GitHub**: control de versiones y entrega.

## 5. Instalación

1. Clona el repositorio y entra en la carpeta:

   ```bash
   git clone https://github.com/<usuario>/editor-imagenes.git
   cd editor-imagenes
   ```

2. (Recomendado) Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

> **Linux (Debian/Ubuntu):** si aparece un error por falta de `tkinter`, instálalo con `sudo apt install python3-tk`. En Windows y macOS ya viene con Python.

## 6. Ejecución

```bash
python main.py
```

En la carpeta `recursos/` hay una imagen de ejemplo (`imagen_ejemplo.png`) para probar la aplicación.

Para ejecutar las pruebas automatizadas:

```bash
pip install -r requirements-dev.txt
pytest
```

## 7. Manual de usuario

> Las capturas se encuentran en `docs/imagenes/`.

### Ventana principal

A la izquierda está el panel de controles (Archivo, Filtros y Transformar); a la derecha, la vista previa; abajo, una barra que informa el resultado de cada acción.

![Ventana principal](docs/imagenes/01_ventana_principal.png)

### Abrir una imagen

Pulsa **Abrir imagen…** (o `Ctrl+O`) y elige un archivo. Mientras no haya una imagen abierta, los demás controles permanecen desactivados.

![Imagen abierta](docs/imagenes/02_imagen_abierta.png)

### Aplicar un filtro

1. Elige el filtro en la lista desplegable.
2. Si el filtro tiene parámetro (desenfoque o contraste), el campo de abajo se activa con el rango permitido. Puedes escribir el valor con punto o con coma.
3. Pulsa **Aplicar filtro**.

![Filtro aplicado](docs/imagenes/03_filtro_aplicado.png)

### Rotar y redimensionar

- **Izquierda 90° / Derecha 90°** giran la imagen.
- Escribe un ancho y un alto enteros y pulsa **Redimensionar**.

![Redimensionar](docs/imagenes/04_redimensionar.png)

### Deshacer y guardar

**Deshacer** vuelve al paso anterior. **Guardar como…** exporta la imagen; el formato se elige por la extensión (`.png`, `.jpg`, `.jpeg`, `.bmp`).

### Errores

Si algo no es válido (por ejemplo, un contraste fuera de rango, un tamaño con letras o un archivo que no es una imagen), aparece un aviso explicando el problema y la imagen actual no se modifica.

![Mensaje de error](docs/imagenes/05_error.png)

## 8. Estructura del proyecto

```
editor_imagenes/
│
├── main.py                      # Punto de entrada: crea los filtros, el editor y la ventana
│
├── modelos/                     # Entidades del dominio
│   ├── __init__.py
│   ├── excepciones.py           # Errores propios (EditorError y derivados)
│   ├── filtros.py               # Filtro (abstracta) y sus clases derivadas
│   └── imagen_editable.py       # Imagen actual + historial para deshacer
│
├── servicios/                   # Lógica de aplicación
│   ├── __init__.py
│   └── editor_imagen.py         # EditorImagen: coordina imagen y filtros, valida datos
│
├── interfaz/                    # Interfaz gráfica (Tkinter)
│   ├── __init__.py
│   ├── ventana_principal.py     # VentanaPrincipal: controles, eventos y callbacks
│   └── visor_imagen.py          # VisorImagen: vista previa de la imagen
│
├── recursos/
│   └── imagen_ejemplo.png       # Imagen para probar la aplicación
│
├── pruebas/
│   ├── test_filtros.py          # Pruebas de los filtros
│   └── test_editor.py           # Pruebas del editor y la imagen editable
│
├── docs/
│   ├── INFORME_TECNICO.md       # Informe técnico del diseño y la construcción
│   └── imagenes/                # Capturas de pantalla
│
├── requirements.txt             # Dependencias de la aplicación (Pillow)
├── requirements-dev.txt         # Dependencias para desarrollo (incluye pytest)
├── pytest.ini                   # Configuración de pytest
├── .gitignore
└── README.md
```

## 9. Autor

- **[Andres Felipe Freite Escobar]**: [3F / Ingeneria de sistemas / institución Universitaria Americana]