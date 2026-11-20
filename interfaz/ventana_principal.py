"""Ventana principal del editor (Tkinter).

La ventana solo se ocupa de mostrar controles, recibir eventos y presentar
resultados. Toda la lógica y las validaciones están en ``EditorImagen``.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from interfaz.visor_imagen import VisorImagen
from modelos.excepciones import EditorError


class VentanaPrincipal(tk.Tk):
    TIPOS_ABRIR = [
        ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
        ("Todos los archivos", "*.*"),
    ]
    TIPOS_GUARDAR = [
        ("PNG", "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("BMP", "*.bmp"),
    ]

    def __init__(self, editor):
        super().__init__()
        self._editor = editor  # asociación: la ventana usa al editor

        self.title("Editor de Imágenes")
        self.geometry("1000x650")
        self.minsize(820, 560)

        self._var_filtro = tk.StringVar()
        self._var_parametro = tk.StringVar()
        self._var_etiqueta_parametro = tk.StringVar()
        self._var_ancho = tk.StringVar()
        self._var_alto = tk.StringVar()
        self._var_estado = tk.StringVar(value="Listo. Abre una imagen para comenzar.")
        self._filtro_con_parametro = False
        self._controles_edicion = []  # widgets que requieren imagen abierta

        self._construir_interfaz()
        self._enlazar_atajos()
        if self._editor.filtros_disponibles:
            self._combo_filtros.current(0)
            self._al_cambiar_filtro()
        self._actualizar_controles()

    # ================================================================
    # Construcción de la interfaz
    # ================================================================
    def _construir_interfaz(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        panel = ttk.Frame(self, padding=10)
        panel.grid(row=0, column=0, sticky="ns")

        self._visor = VisorImagen(self)
        self._visor.grid(row=0, column=1, sticky="nsew")

        barra = ttk.Label(
            self,
            textvariable=self._var_estado,
            anchor="w",
            relief="sunken",
            padding=(8, 3),
        )
        barra.grid(row=1, column=0, columnspan=2, sticky="ew")

        self._construir_seccion_archivo(panel)
        self._construir_seccion_filtros(panel)
        self._construir_seccion_transformar(panel)

    def _seccion(self, padre, titulo):
        marco = ttk.LabelFrame(padre, text=titulo, padding=8)
        marco.pack(fill="x", pady=(0, 10))
        return marco

    def _construir_seccion_archivo(self, panel):
        marco = self._seccion(panel, "Archivo")
        ttk.Button(marco, text="Abrir imagen…  (Ctrl+O)", command=self._al_abrir).pack(
            fill="x", pady=2
        )
        guardar = ttk.Button(
            marco, text="Guardar como…  (Ctrl+S)", command=self._al_guardar
        )
        guardar.pack(fill="x", pady=2)
        self._boton_deshacer = ttk.Button(
            marco, text="Deshacer  (Ctrl+Z)", command=self._al_deshacer
        )
        self._boton_deshacer.pack(fill="x", pady=2)
        self._controles_edicion.append(guardar)

    def _construir_seccion_filtros(self, panel):
        marco = self._seccion(panel, "Filtros")
        self._combo_filtros = ttk.Combobox(
            marco,
            textvariable=self._var_filtro,
            values=self._editor.filtros_disponibles,
            state="readonly",
            width=24,
        )
        self._combo_filtros.pack(fill="x", pady=2)
        self._combo_filtros.bind("<<ComboboxSelected>>", self._al_cambiar_filtro)

        ttk.Label(marco, textvariable=self._var_etiqueta_parametro).pack(
            anchor="w", pady=(6, 0)
        )
        self._entrada_parametro = ttk.Entry(marco, textvariable=self._var_parametro)
        self._entrada_parametro.pack(fill="x", pady=2)
        self._entrada_parametro.bind("<Return>", lambda _e: self._al_aplicar_filtro())

        aplicar = ttk.Button(marco, text="Aplicar filtro", command=self._al_aplicar_filtro)
        aplicar.pack(fill="x", pady=(6, 2))
        self._controles_edicion.extend([self._combo_filtros, aplicar])

    def _construir_seccion_transformar(self, panel):
        marco = self._seccion(panel, "Transformar")

        fila_rotar = ttk.Frame(marco)
        fila_rotar.pack(fill="x", pady=2)
        izquierda = ttk.Button(
            fila_rotar, text="Izquierda 90°", command=lambda: self._al_rotar(90)
        )
        derecha = ttk.Button(
            fila_rotar, text="Derecha 90°", command=lambda: self._al_rotar(-90)
        )
        izquierda.pack(side="left", expand=True, fill="x", padx=(0, 2))
        derecha.pack(side="left", expand=True, fill="x", padx=(2, 0))

        ttk.Label(marco, text="Tamaño (ancho × alto, px):").pack(anchor="w", pady=(8, 0))
        fila_tamano = ttk.Frame(marco)
        fila_tamano.pack(fill="x", pady=2)
        entrada_ancho = ttk.Entry(fila_tamano, textvariable=self._var_ancho, width=7)
        entrada_alto = ttk.Entry(fila_tamano, textvariable=self._var_alto, width=7)
        entrada_ancho.pack(side="left", expand=True, fill="x")
        ttk.Label(fila_tamano, text=" × ").pack(side="left")
        entrada_alto.pack(side="left", expand=True, fill="x")
        for entrada in (entrada_ancho, entrada_alto):
            entrada.bind("<Return>", lambda _e: self._al_redimensionar())

        redimensionar = ttk.Button(
            marco, text="Redimensionar", command=self._al_redimensionar
        )
        redimensionar.pack(fill="x", pady=(6, 2))
        self._controles_edicion.extend(
            [izquierda, derecha, entrada_ancho, entrada_alto, redimensionar]
        )

    def _enlazar_atajos(self):
        self.bind("<Control-o>", self._al_abrir)
        self.bind("<Control-s>", self._al_guardar)
        self.bind("<Control-z>", self._al_deshacer)

    # ================================================================
    # Callbacks (eventos de la interfaz)
    # ================================================================
    def _al_abrir(self, _evento=None):
        ruta = filedialog.askopenfilename(title="Abrir imagen", filetypes=self.TIPOS_ABRIR)
        if not ruta:  # el usuario canceló
            return
        self._ejecutar(
            lambda: self._editor.cargar(ruta),
            f"Imagen cargada: {os.path.basename(ruta)}",
        )

    def _al_guardar(self, _evento=None):
        if not self._editor.hay_imagen:
            self._avisar("Primero debes abrir una imagen.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Guardar imagen como",
            defaultextension=".png",
            filetypes=self.TIPOS_GUARDAR,
        )
        if not ruta:
            return
        self._ejecutar(
            lambda: self._editor.exportar(ruta),
            f"Imagen guardada en: {ruta}",
        )

    def _al_cambiar_filtro(self, _evento=None):
        parametro = self._editor.parametro_de(self._var_filtro.get())
        if parametro is None:
            self._filtro_con_parametro = False
            self._var_etiqueta_parametro.set("Este filtro no tiene parámetros")
            self._var_parametro.set("")
        else:
            etiqueta, minimo, maximo, valor = parametro
            self._filtro_con_parametro = True
            self._var_etiqueta_parametro.set(f"{etiqueta} ({minimo:g} a {maximo:g}):")
            self._var_parametro.set(f"{valor:g}")
        self._actualizar_controles()

    def _al_aplicar_filtro(self):
        nombre = self._var_filtro.get()
        valor = self._var_parametro.get() if self._filtro_con_parametro else None
        self._ejecutar(
            lambda: self._editor.aplicar_filtro(nombre, valor),
            f"Filtro aplicado: {nombre}",
        )

    def _al_rotar(self, grados):
        self._ejecutar(lambda: self._editor.rotar(grados), "Imagen rotada.")

    def _al_redimensionar(self):
        self._ejecutar(
            lambda: self._editor.redimensionar(self._var_ancho.get(), self._var_alto.get()),
            "Imagen redimensionada.",
        )

    def _al_deshacer(self, _evento=None):
        self._ejecutar(self._editor.deshacer, "Cambio deshecho.")

    # ================================================================
    # Utilidades internas
    # ================================================================
    def _ejecutar(self, accion, mensaje_exito):
        """Ejecuta una operación del editor y presenta el resultado.

        Los errores previsibles (``EditorError``) se muestran como aviso;
        cualquier otro error se informa sin cerrar la aplicación.
        """
        try:
            accion()
        except EditorError as error:
            self._avisar(str(error))
        except Exception as error:  # noqa: BLE001 - la interfaz no debe cerrarse
            self._var_estado.set("Ocurrió un error inesperado.")
            messagebox.showerror("Error inesperado", str(error), parent=self)
        else:
            self._refrescar()
            self._var_estado.set(mensaje_exito)

    def _avisar(self, mensaje):
        self._var_estado.set(mensaje)
        messagebox.showwarning("No se pudo completar la acción", mensaje, parent=self)

    def _refrescar(self):
        if self._editor.hay_imagen:
            self._visor.mostrar(self._editor.imagen_actual())
            ancho, alto = self._editor.tamano
            self._var_ancho.set(str(ancho))
            self._var_alto.set(str(alto))
            self.title(f"Editor de Imágenes — {self._editor.nombre_archivo} ({ancho}×{alto})")
        else:
            self._visor.limpiar()
            self.title("Editor de Imágenes")
        self._actualizar_controles()

    def _actualizar_controles(self):
        hay_imagen = self._editor.hay_imagen
        for control in self._controles_edicion:
            self._cambiar_estado(control, hay_imagen)
        self._cambiar_estado(
            self._entrada_parametro, hay_imagen and self._filtro_con_parametro
        )
        self._cambiar_estado(self._boton_deshacer, self._editor.puede_deshacer)

    @staticmethod
    def _cambiar_estado(control, activo):
        control.state(["!disabled"] if activo else ["disabled"])
