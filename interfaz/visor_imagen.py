"""Widget que muestra la vista previa de la imagen."""

import tkinter as tk

from PIL import Image, ImageTk


class VisorImagen(tk.Canvas):
    """Canvas que dibuja una imagen de Pillow ajustada al espacio disponible.

    Hereda de ``tk.Canvas`` y se redibuja solo cuando la ventana cambia de
    tamaño (evento ``<Configure>``).
    """

    MARGEN = 12

    def __init__(self, master, **opciones):
        opciones.setdefault("background", "#2b2b2b")
        opciones.setdefault("highlightthickness", 0)
        super().__init__(master, **opciones)
        self._imagen = None
        self._foto = None  # referencia obligatoria: si se pierde, Tk borra la imagen
        self.bind("<Configure>", self._al_cambiar_tamano)

    def mostrar(self, imagen):
        self._imagen = imagen
        self._dibujar()

    def limpiar(self):
        self._imagen = None
        self._dibujar()

    def _al_cambiar_tamano(self, _evento):
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        ancho_canvas = self.winfo_width()
        alto_canvas = self.winfo_height()
        centro = (ancho_canvas // 2, alto_canvas // 2)

        if self._imagen is None:
            self._foto = None
            self.create_text(
                *centro,
                text="Abre una imagen para comenzar\n(Ctrl+O)",
                fill="#bbbbbb",
                justify="center",
                font=("TkDefaultFont", 12),
            )
            return

        ancho, alto = self._imagen.size
        disponible_x = max(ancho_canvas - 2 * self.MARGEN, 1)
        disponible_y = max(alto_canvas - 2 * self.MARGEN, 1)
        factor = min(disponible_x / ancho, disponible_y / alto, 1.0)
        tamano = (max(int(ancho * factor), 1), max(int(alto * factor), 1))
        if tamano != (ancho, alto):
            vista = self._imagen.resize(tamano, Image.Resampling.LANCZOS)
        else:
            vista = self._imagen
        self._foto = ImageTk.PhotoImage(vista)
        self.create_image(*centro, image=self._foto, anchor="center")
