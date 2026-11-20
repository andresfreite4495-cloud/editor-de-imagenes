"""Punto de entrada del Editor de Imágenes.

Ejecutar con:  python main.py
"""

import sys


def main():
    try:
        from interfaz.ventana_principal import VentanaPrincipal
        from modelos.filtros import (
            FiltroContraste,
            FiltroDesenfoque,
            FiltroGrises,
            FiltroInvertir,
        )
        from servicios.editor_imagen import EditorImagen
    except ImportError as error:
        faltante = getattr(error, "name", None) or str(error)
        print(f"No se pudo iniciar la aplicación: falta el módulo '{faltante}'.")
        if faltante.startswith("PIL"):
            print("Instala las dependencias con:  pip install -r requirements.txt")
        elif faltante.startswith("tkinter"):
            print("Tkinter no está instalado. En Linux (Debian/Ubuntu):  sudo apt install python3-tk")
        sys.exit(1)

    # Los filtros se crean aquí y se entregan al editor (agregación).
    filtros = [
        FiltroGrises(),
        FiltroInvertir(),
        FiltroDesenfoque(),
        FiltroContraste(),
    ]
    editor = EditorImagen(filtros)
    ventana = VentanaPrincipal(editor)
    ventana.mainloop()


if __name__ == "__main__":
    main()
