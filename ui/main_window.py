# ui/main_window.py
import os.path
import re


from gi.repository import Gtk, Gdk, GdkPixbuf
import logging

#from mysql.opentelemetry.importlib_metadata import pass_none

import utils
import webbrowser as wb

from ui.widgets import VisualizadorNotas, EntradaComentarios, Etiquetas, EtiquetasGrupos, FechaRevista, MsgBoxSiNo, MsgBoxInfo, TextEditor, VisualizadorCartas
from services import DBService, RevistaServices, NotaServices, AutorServices, TemaServices, AnalisisService, ServicesArchivoResumen
from models import Revista, Hexagrama, StaffMiembro, Carta, Nota, Autor, Tema, ArchivoResumen
from config import config
from ui.dialogs import DialogCorreo
#from ui.notas_window import DialogNotas

# Config. logging
logger = logging.getLogger(__name__)

class MainWindow(Gtk.Window):

    def __init__(self, app_state):
        Gtk.Window.__init__(self, title="Base de datos de la Revista El Porteño")
        self.set_border_width(10)
        self.app_state = app_state
        self._setup_ui()


    def _setup_ui(self):

        logger.info(f"Creando widgets en MainWindow")

        #Notebook
        self.notebook_page_actual = 0
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # RESOURCES
        if os.path.exists(config.RESUMEN_ICON_PATH):
            self.pixbuf_resume_icon = GdkPixbuf.Pixbuf.new_from_file_at_size(config.RESUMEN_ICON_PATH, 16, 16)


        # CONSTRUCTORES DE UI

        self._setup_revista()
        self._setup_autores()
        self._setup_temas()
        self._setup_analisis()

        # CONECT SIGNALS
        self._connect_signals()

        # PROCEDIMIENtOS INICIALES CARGA DE DATOS Y CONFIG WIDGETS
        self._procedimiento_al_inicio()


    def _setup_revista(self):
        # PÁGINA 1 (P1) - REVISTA
        logger.info(f"--- CREANDO PÁGINA REVISTAS ---")
        self.page_revistas = Gtk.Box(spacing=20)
        self.page_revistas.set_border_width(10)
        self.page_revistas.set_homogeneous(False)
        self.notebook.append_page(self.page_revistas, Gtk.Label(label="Revistas"))

        #P1 - Tres paneles
        self.panel_botones_revistas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.page_revistas.pack_start(self.panel_botones_revistas, False, False, 0)

        self.panel_campos_revistas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.page_revistas.pack_start(self.panel_campos_revistas, True, True, 0)

        self.panel_tapa_y_staff_revistas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.page_revistas.pack_start(self.panel_tapa_y_staff_revistas, True, True, 0)

        #P1 - Panel 1 - Botones
        # Botones - Editar
        self.bt_editar_revista = Gtk.Button(label="Editar")
        self.panel_botones_revistas.pack_start(self.bt_editar_revista, False, False, 0)

        # Botones - Guardar
        self.bt_guardar_revista = Gtk.Button(label="Guardar")
        self.panel_botones_revistas.pack_start(self.bt_guardar_revista, False, False, 0)

        # Botones - Descartar
        self.bt_descartar_cambios_en_revista = Gtk.Button(label="Descartar")
        self.panel_botones_revistas.pack_start(self.bt_descartar_cambios_en_revista, False, False, 0)

        # Botones - Añadir
        self.bt_agregar_nota_en_revista = Gtk.Button(label="Añadir nota")
        self.panel_botones_revistas.pack_start(self.bt_agregar_nota_en_revista, False, False, 0)

        # Botones - Cartas Lector
        self.bt_cartas_en_revista = Gtk.Button(label="Correo Lector")
        self.panel_botones_revistas.pack_start(self.bt_cartas_en_revista, False, False, 0)

        # Label que informa cuántas cartas de correo lector hay
        self.lb_cartas = Gtk.Label()
        self.panel_botones_revistas.pack_start(self.lb_cartas, False, False, 0)

        # Box para completar el espacio nomas
        box_g = Gtk.Box()
        self.panel_botones_revistas.pack_start(box_g, True, True, 0)

        # Botón final
        label = Gtk.Label(label="Buscar por id:")
        self.panel_botones_revistas.pack_start(label, False, False, 0)
        self.ent_buscar_nota_por_id_en_revista = Gtk.Entry()
        self.panel_botones_revistas.pack_start(self.ent_buscar_nota_por_id_en_revista, False, False, 0)

        # PANEL 2
        # P2 - Campo - ROW 1 (Número de la revista - fecha)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # Label
        label = Gtk.Label()
        label.set_markup("<big><b>Número de revista:</b></big>")
        box.pack_start(label, False, False, 0)

        # Spin Button Número de revista
        adj = Gtk.Adjustment(lower=1, upper=134, step_increment=1, page_increment=10)
        self.sb_numero_revista = Gtk.SpinButton()
        self.sb_numero_revista.set_adjustment(adj)
        self.sb_numero_revista.set_numeric(True)
        self.sb_numero_revista.set_digits(0)
        box.pack_start(self.sb_numero_revista, False, False, 0)
        # Label Fecha
        self.fecha_revista = FechaRevista()
        box.pack_start(self.fecha_revista, True, True, 0)
        self.panel_campos_revistas.pack_start(box, False, True, 0)  # Ingresar

        # Campo - ROW 2 (Descripción tapa)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # label
        label = Gtk.Label(label="Tapa:")
        box.pack_start(label, False, True, 0)
        # Entry Tapa
        self.ent_tapa = Gtk.Entry()
        box.pack_start(self.ent_tapa, True, True, 0)
        self.panel_campos_revistas.pack_start(box, False, True, 0)  # Ingresar

        # Campo - ROW 3 (Nota de tapa)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # label
        label = Gtk.Label(label="Nota de Tapa:")
        box.pack_start(label, False, True, 0)
        # Entry Nota de Tapa
        self.ent_nota_de_tapa = Gtk.Entry()
        box.pack_start(self.ent_nota_de_tapa, True, True, 0)
        self.panel_campos_revistas.pack_start(box, False, True, 0)  # Ingresar

        # Campo - ROW 4 (Páginas faltantes - Precio - Formato - Hexagrama)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # label
        label = Gtk.Label(label="Páginas faltantes:")
        box.pack_start(label, False, True, 0)
        # Entry Páginas
        self.ent_paginas_faltantes = Gtk.Entry()
        box.pack_start(self.ent_paginas_faltantes, True, True, 0)
        # label
        label = Gtk.Label(label="Precio:")
        box.pack_start(label, False, True, 0)
        # Entry Precio
        self.ent_precio = Gtk.Entry()
        box.pack_start(self.ent_precio, False, True, 0)
        # label
        label = Gtk.Label(label="Formato:")
        box.pack_start(label, False, True, 0)
        # Formato Combo Box
        ls_items = Gtk.ListStore(str)
        items = ["F", "D", "M", "P"]
        for i in items:
            ls_items.append([i])
        self.cb_formato_archivo = Gtk.ComboBox.new_with_model(ls_items)
        rendered_text = Gtk.CellRendererText()
        self.cb_formato_archivo.pack_start(rendered_text, True)
        self.cb_formato_archivo.add_attribute(rendered_text, "text", 0)
        box.pack_start(self.cb_formato_archivo, False, True, 0)
        # label
        label = Gtk.Label(label="Hexagrama:")
        box.pack_start(label, False, True, 0)
        # Hex_Spin Button
        adj = Gtk.Adjustment(lower=0, upper=64, step_increment=1, page_increment=10)
        self. sb_hexagrama = Gtk.SpinButton()
        self.sb_hexagrama.set_adjustment(adj)
        self.sb_hexagrama.set_numeric(True)
        self.sb_hexagrama.set_digits(0)
        box.pack_start(self.sb_hexagrama, False, False, 0)
        self.panel_campos_revistas.pack_start(box, False, True, 0)  # Ingresar

        # Campo - ROW 5 (Comentarios)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # label
        label = Gtk.Label(label="Comentarios:")
        box.pack_start(label, False, True, 0)
        # Comentarios Text Edit
        self.txt_comentarios_sobre_revistas = EntradaComentarios()
        box.pack_start(self.txt_comentarios_sobre_revistas.empaquetar(), True, True, 0)

        # Label HEX
        self.lb_hexagrama = Gtk.Label(label="")
        box.pack_start(self.lb_hexagrama, False, True, 0)
        self.panel_campos_revistas.pack_start(box, False, True, 0)  # Ingresar

        # Campo - ROW 6 (Visualizador)
        self.vn_revista = VisualizadorNotas(revista=False, autor=True, icon=self.pixbuf_resume_icon)
        self.panel_campos_revistas.pack_start(self.vn_revista, True, True, 0)


        # PANEL 3
        # Imágen de Tapa
        self.im_tapa = Gtk.Image()
        self.eventbox_im_tapa = Gtk.EventBox()
        self.eventbox_im_tapa.add(self.im_tapa)
        self.panel_tapa_y_staff_revistas.pack_start(self.eventbox_im_tapa, False, True, 0)
        # Staff
        self.lb_staff = Gtk.Label()
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_border_width(3)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lb_staff)
        self.panel_tapa_y_staff_revistas.pack_start(scroll, True, True, 0)
        # Boton Staff
        self.bt_staff = Gtk.Button(label="Modificar Staff")
        self.panel_tapa_y_staff_revistas.pack_start(self.bt_staff, False, True, 0)

        logger.info(f"--- FINALIZADA PÁGINA REVISTAS ---")

    def _setup_autores(self):

        # PÁGINA 2 (P2) - AUTORES

        logger.info(f"--- CREANDO PÁGINA AUTORES ---")

        self.page_autores = Gtk.Box(spacing=20)
        self.page_autores.set_border_width(10)
        self.page_autores.set_homogeneous(False)
        self.notebook.append_page(self.page_autores, Gtk.Label(label="Autorxs"))

        #Dos paneles, Lista de autores(izq), campos(der)

        #PANELES - Config
        self.panel_autores_autores = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.page_autores.pack_start(self.panel_autores_autores, True, True, 0)

        self.panel_campos_autores = Gtk.Grid()
        self.panel_campos_autores.set_row_spacing(5)
        self.panel_campos_autores.set_column_spacing(5)
        self.page_autores.pack_start(self.panel_campos_autores, True, True, 0)

        self.panel_botones_autores = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.page_autores.pack_start(self.panel_botones_autores, True, True, 0)


        #PANEL IZQ

        # Campos de búsqueda
        self.ent_buscar_autor = Gtk.SearchEntry()
        self.panel_autores_autores.pack_start(self.ent_buscar_autor, False, False, 0)

        # Listado de autores
        self.list_autores = Gtk.TreeView()
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_border_width(3)
        scroll.set_size_request(340, 750)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scroll.add(self.list_autores)
        ls = Gtk.ListStore(int, str)
        ls.append([0, "No cargado"])
        self.list_autores.set_model(ls)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("id", renderer, text=0)
        column.set_resizable(False)
        column.set_visible(False)
        self.list_autores.append_column(column)
        column = Gtk.TreeViewColumn("Nombre", renderer, text=1)
        column.set_resizable(False)
        column.set_visible(True)
        self.list_autores.append_column(column)
        self.list_autores.set_headers_visible(False)
        self.list_autores.set_activate_on_single_click(True)
        self.list_autores.set_enable_search(False)

        self.panel_autores_autores.pack_start(scroll, True, True, 0)

        #PANEL CENTRAL

        # ROW1 (id)
        self.ent_id_autor = Gtk.Entry()
        self.ent_id_autor.set_editable(False)

        #ROW2 (Nombre)
        self.ent_nombre_autor = Gtk.Entry()

        #ROW3 (Apellido)
        self.ent_apellido_autor = Gtk.Entry()

        #ROW4 (Genero)
        ls_items = Gtk.ListStore(str, str)
        items = (["Fem", "Femenino"], ["Masc", "Masculino"], ["NoA","No aplica"], ["Otrx","Otrx"])
        for i in items:
            ls_items.append(i)
        self.cb_genero_autor = Gtk.ComboBox.new_with_model(ls_items)
        rendered_text = Gtk.CellRendererText()
        self.cb_genero_autor.pack_start(rendered_text, True)
        self.cb_genero_autor.add_attribute(rendered_text, "text", 1)
        self.cb_genero_autor.set_active(-1)

        #RO5 (Comentarios)
        self.txt_comentarios_sobre_autores = EntradaComentarios()

        #%06
        self.lb_n_notas_autores = Gtk.Label("")
        self.lb_n_notas_autores.set_halign(Gtk.Align.START)

        #ROW7 (Visualizador de notas)
        self.vn_autor = VisualizadorNotas(revista=True, autor=False, icon= self.pixbuf_resume_icon)

        #ROW1
        self.panel_campos_autores.attach(Gtk.Label(label="id:"), 0, 0, 1, 1)
        self.panel_campos_autores.attach(self.ent_id_autor, 1, 0, 1, 1)
        #ROW2
        self.panel_campos_autores.attach(Gtk.Label(label="Nombre:"), 0, 1, 1, 1)
        self.panel_campos_autores.attach(self.ent_nombre_autor, 1, 1, 1, 1)
        #ROW3
        self.panel_campos_autores.attach(Gtk.Label(label="Apellido:"), 0, 2, 1, 1)
        self.panel_campos_autores.attach(self.ent_apellido_autor, 1, 2, 1, 1)
        #ROW4
        self.panel_campos_autores.attach(Gtk.Label(label="Género:"), 0, 3, 1, 1)
        self.panel_campos_autores.attach(self.cb_genero_autor, 1, 3, 1, 1)
        #ROW5
        self.panel_campos_autores.attach(Gtk.Label(label="Comentarios:"), 0, 4, 1, 1)
        self.panel_campos_autores.attach(self.txt_comentarios_sobre_autores.empaquetar(), 1, 4, 1, 1)
        #RO"6
        self.panel_campos_autores.attach(self.lb_n_notas_autores, 0,5,2,1)
        #ROW7
        self.panel_campos_autores.attach(self.vn_autor, 0, 6, 2, 1)



        #PANEL DERECHO
        #Botones
        self.bt_editar_autor = Gtk.Button(label="Editar")
        self.bt_editar_autor.set_size_request(100, -1)
        self.bt_guardar_autor = Gtk.Button(label="Guardar")
        self.bt_guardar_autor.set_size_request(100, -1)
        self.bt_descartar_cambios_en_autor = Gtk.Button(label="Descartar")
        self.bt_descartar_cambios_en_autor.set_size_request(100, -1)

        self.panel_botones_autores.pack_start(self.bt_editar_autor, False, True, 5)
        self.panel_botones_autores.pack_start(self.bt_guardar_autor, False, True, 0)
        self.panel_botones_autores.pack_start(self.bt_descartar_cambios_en_autor, False, True, 5)

        logger.info(f"--- FINALIZADA PÁGINA AUTORES ---")

    def _setup_temas(self):


        logger.info(f"--- CREANDO PÁGINA TEMAS ---")

        self.page_temas = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.page_temas.set_border_width(10)
        self.page_temas.set_homogeneous(False)
        self.panel_temas_temas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.panel_seleccion_temas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.notebook.append_page(self.page_temas, Gtk.Label(label="Temas"))
        self.panel_temas = Gtk.Grid()
        self.panel_temas.set_row_spacing(5)
        self.panel_temas.set_column_spacing(5)

        self.page_temas.pack_start(self.panel_temas, True, True, 0)

        self.ent_buscar_tema = Gtk.SearchEntry()

        ## -listado temas
        self.list_temas = Gtk.TreeView()
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_border_width(3)
        scroll.set_size_request(340, 750)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        scroll.add(self.list_temas)
        ls = Gtk.ListStore(int, str)
        ls.append([0, "No Cargado"])
        self.list_temas.set_model(ls)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("id", renderer, text=0)
        column.set_resizable(False)
        column.set_visible(False)
        self.list_temas.append_column(column)
        column = Gtk.TreeViewColumn("nombre", renderer, text=1)
        column.set_resizable(False)
        column.set_visible(True)
        self.list_temas.append_column(column)
        self.list_temas.set_headers_visible(False)
        self.list_temas.set_enable_search(False)

        label_temas_seleccionados = Gtk.Label()
        label_temas_seleccionados.set_markup("<big><b>Temas seleccionados:</b></big>")
        self.fb_temas_seleccionados = Etiquetas()
        self.fb_temas_seleccionados.set_halign(Gtk.Align.START)
 #       self.panel_temas_temas.pack_start(self.fb_temas, True, True, 0)

        label = Gtk.Label()
        label.set_markup("<big><b>Notas por Temas:</b></big>")
#        self.panel_seleccion_temas.pack_start(label, False, False, 0)

        self.vn_temas = VisualizadorNotas(revista=True, autor=True, icon= self.pixbuf_resume_icon)
 #       self.panel_seleccion_temas.pack_start(self.vn_temas, True, True, 0)

        self.panel_temas.attach(self.ent_buscar_tema, 0, 0, 1, 1)
        self.panel_temas.attach(scroll, 0, 1, 1, 3)
        self.panel_temas.attach(label_temas_seleccionados, 1, 0, 1, 1)
        self.panel_temas.attach(self.fb_temas_seleccionados, 1, 1, 1, 1)
        self.panel_temas.attach(label, 1,2,1,1)
        self.panel_temas.attach(self.vn_temas, 1, 3, 1, 1)


        logger.info(f"--- FINALIZADA PÁGINA TEMAS ---")

    def _setup_analisis(self):
        # PÁGINA # (P4) - ANALISIS

        logger.info(f"--- CREANDO PÁGINA ANALISIS ---")

        self.page_analisis = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.page_analisis.set_border_width(10)
        self.page_analisis.set_homogeneous(False)
        self.panel_grupos_analisis = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.panel_notas_analisis = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.notebook.append_page(self.page_analisis, Gtk.Label(label="Grupos para análisis"))
        self.page_analisis.pack_start(self.panel_grupos_analisis, True, True, 0)
        self.page_analisis.pack_start(self.panel_notas_analisis, True, True, 0)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.ent_agregar_grupo_analisis = Gtk.Entry()
        box.pack_start(self.ent_agregar_grupo_analisis, True, True, 0)
        self.bt_crear_grupo_analisis = Gtk.Button(label="+")
        box.pack_start(self.bt_crear_grupo_analisis, False, False, 0)
        self.panel_grupos_analisis.pack_start(box, False, False, 0)

        ## -listado Grupos

        self.fb_grupos = EtiquetasGrupos()
        self.panel_grupos_analisis.pack_start(self.fb_grupos, True, True, 0)

        ## - Cargar id en un grupo
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        label = Gtk.Label("id a cargar: ")
        box.pack_start(label, False, False, 2)
        self.ent_id_analisis = Gtk.Entry()
        box.pack_start(self.ent_id_analisis, False, False, 2)
        self.bt_carga_preliminar_id_analisis = Gtk.Button(label="Nota ->")
        box.pack_start(self.bt_carga_preliminar_id_analisis, False, False, 2)
        self.lb_nota_a_cargar_analisis = Gtk.Label("[Nota a cargar]")
        box.pack_start(self.lb_nota_a_cargar_analisis, True, True, 2)
        self.bt_x_carga_id = Gtk.Button(label="X")
        style_context = self.bt_x_carga_id.get_style_context()
        style_context.add_class("button-x-red")
        box.pack_start(self.bt_x_carga_id, False, False, 0)
        ls_items = Gtk.ListStore(int, str)
        self.cb_grupo_analisis = Gtk.ComboBox.new_with_model(ls_items)
        rendered_text = Gtk.CellRendererText()
        self.cb_grupo_analisis.pack_start(rendered_text, True)
        self.cb_grupo_analisis.add_attribute(rendered_text, "text", 1)

        box.pack_start(self.cb_grupo_analisis, False, True, 0)
        self.bt_carga_definitiva_nota_analisis = Gtk.Button(label="cargar")
        box.pack_start(self.bt_carga_definitiva_nota_analisis, False, False, 2)

        self.panel_notas_analisis.pack_start(box, False, True, 2)

        self.lb_titulo_grupos_de_analisis = Gtk.Label()
        self.lb_titulo_grupos_de_analisis.set_markup("<big><b>Agrupamiento de notas para el análisis:</b></big>")
        self.panel_notas_analisis.pack_start(self.lb_titulo_grupos_de_analisis, False, False, 0)

        self.vn_analisis = VisualizadorNotas(revista=True, autor=True, icon= self.pixbuf_resume_icon)
        self.panel_notas_analisis.pack_start(self.vn_analisis, True, True, 0)

        self.lb_titulo_cartas_grupos_de_analisis = Gtk.Label()
        self.lb_titulo_cartas_grupos_de_analisis.set_markup("<big><b>Agrupamiento de cartas para el análisis:</b></big>")
        self.panel_notas_analisis.pack_start(self.lb_titulo_cartas_grupos_de_analisis, False, False, 0)

        self.vc_analisis = VisualizadorCartas(icon=self.pixbuf_resume_icon)
        self.panel_notas_analisis.pack_start(self.vc_analisis, True, True, 0)

        logger.info(f"--- FINALIZADA PÁGINA ANALISIS ---")

        logger.info(f"--- INICIO PROCEDIMIENTOS INCIALES ---")

        logger.info(f"--- FIN DE MAIN WINDOW ---")

    def _connect_signals(self):
        self.notebook.connect("switch-page", self.on_switch_page) #Notebook cambiar pag
        self.bt_editar_revista.connect("clicked", self.bt_editar_revista_clicked) #P1-Botón Editar_Click
        self.bt_guardar_revista.connect("clicked", self.bt_guardar_revista_clicked) #P1 - Botón Guardar_Click
        self.bt_descartar_cambios_en_revista.connect("clicked", self.bt_descartar_cambios_en_revista_clicked) #P1 - Botón descartar_Click
        self.bt_agregar_nota_en_revista.connect("clicked", self.bt_agregar_nota_en_revista_clicked) #P1 - Botón Agregar_Click
        self.bt_cartas_en_revista.connect("clicked", self.bt_cartas_en_revista_clicked) #P1 - Botón Cartas_Click
        self.ent_buscar_nota_por_id_en_revista.connect("activate", self.ent_buscar_id_activate) #P1 - Enter Buscar Id
        self.sb_numero_revista.connect("value-changed", self.sb_numero_revista_valuechanged) #P1 Spin buton change
        self.sb_hexagrama.connect("value-changed", self.sb_hexagrama_valuechanged) #P1 Hexagrama change
        self.vn_revista.tn.connect("row-activated", self.vn_revista_row_activate) #P1 Visualizador de notas
        self.vn_revista.connect("new_resumen", self.on_new_archivo_resumen)
        self.eventbox_im_tapa.connect("button_press_event", self.eventbox_im_tapa_clicked) #P1 Tapa click
        self.bt_staff.connect("clicked", self.bt_staff_clicked) #P1 Staff Click
        self.ent_buscar_autor.connect("changed", self.ent_buscar_autor_changed) #P2 Buscar Autor
        self.list_autores.connect("row-activated", self.list_autores_row_activate) #P2 Listado de autores, activar
        self.vn_autor.tn.connect("row-activated", self.vn_autor_row_activate) #P2 Visualizador de notas
        self.vn_autor.connect("new_resumen", self.on_new_archivo_resumen)
        self.bt_editar_autor.connect("clicked", self.bt_editar_autor_clicked) #P2 Botón editar autor
        self.bt_guardar_autor.connect("clicked", self.bt_guardar_autor_clicked) #P2 Botón guardar autor
        self.bt_descartar_cambios_en_autor.connect("clicked", self.bt_descartar_cambios_en_autor_clicked) #P2 Botón descartar cambios
        self.ent_buscar_tema.connect("changed", self.ent_buscar_tema_changed) #P3 Buscar temas
        self.list_temas.connect("row-activated", self.list_temas_row_activated)
        self.fb_temas_seleccionados.connect("button-removed", self.fb_temas_on_tag_removed)
        self.vn_temas.tn.connect("row-activated", self.vn_temas_row_activated) #P3 Listado de visualización de notas según temas
        self.vn_temas.connect("new_resumen", self.on_new_archivo_resumen)
        self.ent_agregar_grupo_analisis.connect("activate", self.ent_agregar_grupo_analisis_activate) #P4 Crear categorías
        self.bt_crear_grupo_analisis.connect("clicked", self.bt_crear_grupo_analisis_clicked) #P4 Boton crear categoría
        self.fb_grupos.connect("tags-changed", self.fb_grupos_on_tag_selected) #P4 ACtivar etiqueta
        self.ent_id_analisis.connect("activate", self.ent_id_analisis_activate) #P4 Cargar id
        self.bt_carga_preliminar_id_analisis.connect("clicked", self.bt_cargar_id_analisis_clicked) #P4 Cargar id
        self.bt_x_carga_id.connect("clicked", self.bt_x_carga_id_clicked)
        self.bt_carga_definitiva_nota_analisis.connect("clicked", self.bt_agrupar_nota_analisis_clicked) #P4 Agrupa nota
        self.vn_analisis.tn.connect("row_activated", self.vn_analisis_row_activate)
        self.vn_analisis.tn.connect("key-press-event", self.vn_analisis_key_press_event)
        self.vn_analisis.connect("new_resumen", self.on_new_archivo_resumen)
        self.vc_analisis.tc.connect("row_activated", self.vc_analisis_row_activate)
        self.vc_analisis.connect("new_resumen", self.on_new_archivo_resumen)
        self.connect("destroy", self.on_destroy) #Terminar Main window

    # METODOS DE ORQUESTACIÓN Y LÓGICA DE LA UI

    def _procedimiento_al_inicio(self):
        DBService.configuración_inicial()
        last_id = DBService.get_id_ultima_revista_abierta()
        self.set_widget_revista_como_editables(False)
        self.set_widgets_autores_como_editables(False)
        self.set_widgets_analisis_como_editables(False)
        self.actualizar_revista(last_id)
        self.actualizar_lista_autores()
        self.actualizar_lista_temas()
        self.actualizar_fb_grupos_analisis()

    # Correspondiente a la sección REVISTAS

    def actualizar_revista(self, id_revista: int):
        self.cargar_revista_en_app_state(id_revista)
        self.actualizar_widgets_revista()

    def cargar_revista_en_app_state(self, id_revista: int):
        revista = RevistaServices.get_revista(id_revista)
        RevistaServices.cargar_staff_completo(revista)
        RevistaServices.cargar_notas(revista)
        RevistaServices.cargar_correo(revista)
        RevistaServices.cargar_hexagrama(revista)
        self.app_state.revista_seleccionada = revista

    def set_widget_revista_como_editables(self, editable: bool):

        if editable:
            self.app_state.revista_edicion_activa = True
            self.bt_editar_revista.set_sensitive(False)
            self.bt_guardar_revista.set_sensitive(True)
            self.bt_descartar_cambios_en_revista.set_sensitive(True)
            self.bt_agregar_nota_en_revista.set_sensitive(False)
            self.bt_cartas_en_revista.set_sensitive(False)
            self.ent_buscar_nota_por_id_en_revista.set_editable(False)
            self.sb_numero_revista.set_sensitive(False)
            self.ent_tapa.set_editable(True)
            self.ent_nota_de_tapa.set_editable(True)
            self.ent_paginas_faltantes.set_editable(True)
            self.ent_precio.set_editable(True)
            self.cb_formato_archivo.set_sensitive(True)
            self.sb_hexagrama.set_sensitive(True)
            self.txt_comentarios_sobre_revistas.tv.set_editable(True)
            self.bt_staff.set_sensitive(False)
            self.notebook.set_show_tabs(False)

        else:
            self.app_state.revista_edicion_activa = False
            self.bt_editar_revista.set_sensitive(True)
            self.bt_guardar_revista.set_sensitive(False)
            self.bt_descartar_cambios_en_revista.set_sensitive(False)
            self.bt_agregar_nota_en_revista.set_sensitive(True)
            self.bt_cartas_en_revista.set_sensitive(True)
            self.ent_buscar_nota_por_id_en_revista.set_editable(True)
            self.sb_numero_revista.set_sensitive(True)
            self.ent_tapa.set_editable(False)
            self.ent_nota_de_tapa.set_editable(False)
            self.ent_paginas_faltantes.set_editable(False)
            self.ent_precio.set_editable(False)
            self.cb_formato_archivo.set_sensitive(False)
            self.sb_hexagrama.set_sensitive(False)
            self.txt_comentarios_sobre_revistas.tv.set_editable(False)
            self.bt_staff.set_sensitive(True)
            self.notebook.set_show_tabs(True)

    def actualizar_widgets_revista(self):
        self.limpiar_widgets_revista()
        self.cargar_widgets_revista(self.app_state.revista_seleccionada)

    def limpiar_widgets_revista(self):
        self.fecha_revista.mostrar_vacio()
        self.ent_tapa.set_text("")
        self.ent_nota_de_tapa.set_text("")
        self.ent_paginas_faltantes.set_text("")
        self.ent_precio.set_text("")
        self.cb_formato_archivo.set_active(-1)
        self.sb_hexagrama.set_value(0)
        self.txt_comentarios_sobre_revistas.borrar_contenido()
        self.lb_staff.set_text("")
        self.lb_cartas.set_text("")
        self.im_tapa.clear()
        self.vn_revista.borrar_contenido()
        self.fecha_revista.mostrar_vacio()

    def cargar_widgets_revista(self, revista: Revista):
        if not self.app_state.sb_numero_revista_signal_activo: #Comprobaciones para evitar un loop, poder entender de dónde vienve el cambio
            self.app_state.sb_numero_revista_actualizado_desde_sistema = True
            if int(self.sb_numero_revista.get_value()) != revista.id:
                self.sb_numero_revista.set_value(revista.id)
            self.app_state.sb_numero_revista_actualizado_desde_sistema = False

        self.fecha_revista.cargar_texto(revista.fecha)
        self.fecha_revista.definir_estado(revista.estado, self.app_state.revista_edicion_activa)
        self.ent_tapa.set_text(revista.tapa)
        self.ent_nota_de_tapa.set_text(revista.nota_tapa)
        self.ent_paginas_faltantes.set_text(revista.paginas_faltantes)
        self.ent_precio.set_text(revista.precio)
        ls = self.cb_formato_archivo.get_model()
        for i, row in enumerate(ls):
            if row[0] == revista.formato: self.cb_formato_archivo.set_active(i)
        self.actualizar_hexagrama(revista.hexagrama)
        self.txt_comentarios_sobre_revistas.set_text(revista.comentarios)
        self.actualizar_staff_en_revista(revista.staff)
        self.actualizar_texto_carta(revista.correo)
        self.cargar_imagen_tapa(revista.id)
        self.vn_revista.cargar_notas(revista.notas)

    def actualizar_hexagrama(self, hex: Hexagrama):
        if int(self.sb_hexagrama.get_value()) != hex.numero:
            self.sb_hexagrama.set_value(hex.numero)
            self.lb_hexagrama.set_markup(f"<b>{hex.lineas}</b>")
            self.lb_hexagrama.set_visible(True) if hex.numero > 0 else self.lb_hexagrama.set_visible(False)

    def actualizar_staff_en_revista(self, staff: list[StaffMiembro]):

        texto = "STAFF REVISTA:\n\n"

        if not staff:
            texto = "Staff no cargado"
        else:
            for integrante in staff:
                texto += f"{integrante.posicion}: {utils.get_nombre_completo(integrante)}\n"

        self.lb_staff.set_text(texto)

    def actualizar_texto_carta(self, correo: list[Carta]):
        numero_cartas = len(correo)
        self.lb_cartas.set_markup(f"<small>{numero_cartas} cartas disponibles </small>")

    def cargar_imagen_tapa(self, id_revista: int):
        ruta = f"Tapas/{id_revista}.png"
        if os.path.exists(ruta):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(ruta, 250, 250)
            self.im_tapa.set_from_pixbuf(pixbuf)
        else:
            self.im_tapa.clear()

    def get_data_from_widgets_revista(self):
        tapa = self.ent_tapa.get_text()
        nota_tapa = self.ent_nota_de_tapa.get_text()
        paginas_faltantes = self.ent_paginas_faltantes.get_text()
        precio = self.ent_precio.get_text()
        row = self.cb_formato_archivo.get_active()
        formato = self.cb_formato_archivo.get_model()[row][0]
        hexagrama = int(self.sb_hexagrama.get_value())
        comentarios = self.txt_comentarios_sobre_revistas.get_text()

        data = {
            'tapa': tapa,
            'nota_tapa': nota_tapa,
            'hexagrama': hexagrama,
            'paginas_faltantes': paginas_faltantes,
            'formato_en_archivo': formato,
            'comentarios': comentarios,
            'precio_nominal': precio
                }

        return data

    def get_data_from_app_state_revista(self):
        data = {
            'tapa': self.app_state.revista_seleccionada.tapa,
            'nota_tapa': self.app_state.revista_seleccionada.nota_tapa,
            'hexagrama': self.app_state.revista_seleccionada.hexagrama.numero,
            'paginas_faltantes': self.app_state.revista_seleccionada.paginas_faltantes,
            'formato_en_archivo': self.app_state.revista_seleccionada.formato,
            'comentarios': self.app_state.revista_seleccionada.comentarios,
            'precio_nominal': self.app_state.revista_seleccionada.precio
                }
        return data

    def go_to_nota(self, id_nota):
        nota_dict = NotaServices.get_nota_por_id_nota(id_nota)
        if not nota_dict:
            MsgBoxInfo(f"El id {id_nota} no corresponde a una nota existente")
            return
        nota = Nota(nota_dict)
        if nota.revista != self.app_state.revista_seleccionada.id:
            self.actualizar_revista(nota.revista)
        self.vn_revista.seleccionar_nota_segun_id(id_nota)


    def run_text_editor_in_window(self, archivo_resumen: ArchivoResumen = None, nota_id: int = 0, desde: str = "revista", tipo: str = "nota"):

        if archivo_resumen:
            titulo_ventana = archivo_resumen.titulo
        else:
            titulo_ventana = "Editor de resúmenes y análisis"
            archivo_resumen = ArchivoResumen({"id":0, "nota_id": nota_id, "titulo": "", "cuerpo_texto": ""})


        window = Gtk.Window(title=titulo_ventana)
        window.set_default_size(800, 600)


        editor = TextEditor(tipo=tipo)
        editor.cargar_resumen(archivo_resumen)
        window.add(editor)
        window.show_all()

        window.connect("destroy", self.on_editor_window_destroy, editor, desde, tipo)


    # Correspondiente a la sección Autores

    def set_widgets_autores_como_editables(self, editable: bool):

        if editable:
            self.app_state.autores_edicion_activa = True
            self.bt_editar_autor.set_sensitive(False)
            self.bt_descartar_cambios_en_autor.set_sensitive(True)
            self.bt_guardar_autor.set_sensitive(True)
            self.ent_nombre_autor.set_editable(True)
            self.ent_apellido_autor.set_editable(True)
            self.cb_genero_autor.set_sensitive(True)
            self.txt_comentarios_sobre_autores.tv.set_editable(True)
            self.ent_buscar_autor.set_editable(False)
            self.list_autores.set_sensitive(False)
            self.notebook.set_show_tabs(False)

        else:
            self.app_state.autores_edicion_activa = False
            self.bt_editar_autor.set_sensitive(True)
            self.bt_descartar_cambios_en_autor.set_sensitive(False)
            self.bt_guardar_autor.set_sensitive(False)
            self.ent_nombre_autor.set_editable(False)
            self.ent_apellido_autor.set_editable(False)
            self.cb_genero_autor.set_sensitive(False)
            self.txt_comentarios_sobre_autores.tv.set_editable(False)
            self.ent_buscar_autor.set_editable(True)
            self.list_autores.set_sensitive(True)
            self.notebook.set_show_tabs(True)

    def actualizar_lista_autores(self, texto_busqueda: str = ""): #ACTUALIZA LISTADO DE AUTORES

        ls = self.list_autores.get_model()
        ls.clear()

        autores = AutorServices.get_lista_autores_por_nombre(texto_busqueda)

        if autores:
            for elemento in autores:
                autor = Autor(elemento)
                ls.append([autor.id, utils.get_nombre_completo(autor)])
        else:
            ls.append([0, "No hay resultados"])

    def actualizar_autor(self, autor: Autor): #ACTUALIZA WIDGETS AUTORES CUANDO SE CARGA UN AUTOR EN LISTADO DE AUTORES
        self.cargar_autor_en_app_state(autor)
        self.actualizar_widgets_autor()

    def actualizar_widgets_autor(self):
        autor = self.app_state.autor_seleccionado
        self.limpiar_widgets_autores()
        self.cargar_widgets_autores(autor)

    def cargar_autor_en_app_state(self, autor: Autor):
        self.app_state.autor_seleccionado = autor

    def limpiar_widgets_autores(self):
        self.ent_id_autor.set_text("")
        self.ent_nombre_autor.set_text("")
        self.ent_apellido_autor.set_text("")
        self.cb_genero_autor.set_active(-1)
        self.txt_comentarios_sobre_autores.borrar_contenido()
        self.lb_n_notas_autores.set_text("")
        self.vn_autor.tn.get_model().clear()

    def cargar_widgets_autores(self, autor: Autor):
        self.ent_id_autor.set_text(str(autor.id))
        self.ent_nombre_autor.set_text(autor.nombre)
        self.ent_apellido_autor.set_text(autor.apellido)
        ls = self.cb_genero_autor.get_model()
        for i, row in enumerate(ls):
            if row[0] == autor.genero: self.cb_genero_autor.set_active(i)
        self.txt_comentarios_sobre_autores.set_text(autor.comentarios)
        lista_notas = AutorServices.get_notas_de_autor(autor.id)
        self.lb_n_notas_autores.set_markup(f"<span foreground='#d8dee9'><small><i>{autor.apellido} tiene {len(lista_notas)} notas cargadas</i></small></span>")
        notas = utils.to_nota(lista_notas)
        self.vn_autor.cargar_notas(notas)

    def get_data_from_app_state_autor(self):
        data = {
            'nombre': self.app_state.autor_seleccionado.nombre,
            'apellido': self.app_state.autor_seleccionado.apellido,
            'genero': self.app_state.autor_seleccionado.genero,
            'comentarios': self.app_state.autor_seleccionado.comentarios
        }
        return data

    def get_data_from_widgets_autores(self):
        nombre = self.ent_nombre_autor.get_text()
        apellido = self.ent_apellido_autor.get_text()
        row = self.cb_genero_autor.get_active()
        genero = self.cb_genero_autor.get_model()[row][0]
        comentarios = self.txt_comentarios_sobre_autores.get_text()

        data = {
            'nombre': nombre,
            'apellido': apellido,
            'genero': genero,
            'comentarios': comentarios
        }
        return data

    def seleccionar_autor_en_lista_autores(self, id_autor):
        model = self.list_autores.get_model()
        for i, row in enumerate(model):
            if int(id_autor) == row[0]:
                self.list_autores.set_cursor(Gtk.TreePath(i))


    # Relacionados a Temas

    def actualizar_lista_temas(self, busqueda: str = ""):

        ls = self.list_temas.get_model()
        ls.clear()
        tags = self.fb_temas_seleccionados.get_selected_tags()

        if len(tags) == 0:
            tabla_temas = TemaServices.get_temas_busqueda(busqueda)

            if tabla_temas:
                temas = utils.to_tema(tabla_temas)
                for tema in temas:
                    ls.append([tema.id, tema.tema])
            else:
                ls.append([0, "No hay resultados"])
        else:
            model = self.vn_temas.tn.get_model()
            id_notas = []
            for nota in model:
                id_notas.append(nota[0])
            tabla_temas = TemaServices.get_temas_segun_tags_seleccionados(busqueda=busqueda, id_notas=id_notas)

            if tabla_temas:
                temas = utils.to_tema(tabla_temas)
                for tema in temas:
                    if not utils.is_in_tags(tema, self.fb_temas_seleccionados.tags):
                        ls.append([tema.id, tema.tema])
                if not len(ls):
                    ls.append(0, "No hay resultado")


    def cargar_notas_en_visor_nota_temas(self):

        self.vn_temas.borrar_contenido()

        temas_seleccionados = self.fb_temas_seleccionados.get_selected_tags()
        lista_notas = TemaServices.get_notas_por_temas_seleccionados(temas_seleccionados)
        notas = utils.to_nota(lista_notas)
        self.vn_temas.cargar_notas(notas)

# Relacionados a Grupo

    def set_widgets_analisis_como_editables(self, editable):
        if editable:
            self.ent_id_analisis.set_editable(False)
            self.bt_carga_preliminar_id_analisis.set_sensitive(False)
            self.cb_grupo_analisis.set_sensitive(True)
            self.bt_x_carga_id.set_visible(True)
            self.bt_carga_definitiva_nota_analisis.set_sensitive(True)
        else:
            self.ent_id_analisis.set_editable(True)
            self.bt_carga_preliminar_id_analisis.set_sensitive(True)
            self.cb_grupo_analisis.set_sensitive(False)
            self.bt_x_carga_id.set_visible(False)
            self.bt_carga_definitiva_nota_analisis.set_sensitive(False)

    def actualizar_fb_grupos_analisis(self):
        grupos = AnalisisService.get_grupos_analisis()
        self.fb_grupos.cargar_botones(grupos)
        self.cargar_cb_con_cambio_en_botones()


    def cargar_cb_con_cambio_en_botones(self):
        ls = self.cb_grupo_analisis.get_model()
        ls.clear()
        grupos = self.fb_grupos.get_botones()
        for grupo in grupos:
            ls.append([grupo.id, grupo.categoria])

    def actualizar_notas_analisis(self, id_tag):
        notas = AnalisisService.get_notas_por_grupo_analisis(id_tag)
        notas = utils.to_nota(notas)
        self.vn_analisis.cargar_notas(notas)

    def actualizar_cartas_analisis(self, id_tag):
        cartas = AnalisisService.get_cartas_por_grupo_analisis(id_tag)
        cartas = utils.to_cartas(cartas)
        self.vc_analisis.actualizar(id_tag)
        self.vc_analisis.cargar_cartas(cartas, id_tag)

    def resetear_carga_nota_en_grupo_analisis(self):
        self.app_state.nota_a_cargar_en_grupo_analisis = None
        self.up_label_nota_a_cargar_en_grupo_analisis()
        self.set_widgets_analisis_como_editables(False)

    def up_label_nota_a_cargar_en_grupo_analisis(self, label: str = ""):
        if len(label) > 70:
            label = label[0:70] + "..."
        self.lb_nota_a_cargar_analisis.set_markup(f"<b>{label}</b>")

    #MANEJADORES DE SEÑALES

    def on_switch_page(self, widget, widget_page, page_num):
        pass

    #Page Revistas (P1)

    def bt_editar_revista_clicked(self, widget):
        self.set_widget_revista_como_editables(True)
        self.fecha_revista.definir_estado(self.app_state.revista_seleccionada.estado, self.app_state.revista_edicion_activa)

    def bt_guardar_revista_clicked(self, widget):
        data_original = self.get_data_from_app_state_revista()
        data_actual = self.get_data_from_widgets_revista()
        id_revista = self.app_state.revista_seleccionada.id
        if not utils.changes_were_made(data_original, data_actual):
            self.set_widget_revista_como_editables(False)
            self.fecha_revista.definir_estado(estado=self.app_state.revista_seleccionada.estado)
        else:
            RevistaServices.guardar_cambios_revista(id_revista, data_actual)
            self.set_widget_revista_como_editables(False)
            self.actualizar_revista(id_revista)

    def bt_descartar_cambios_en_revista_clicked(self, widget):
        data_original = self.get_data_from_app_state_revista()
        data_actual = self.get_data_from_widgets_revista()
        if utils.changes_were_made(data_original, data_actual):
            pregunta = MsgBoxSiNo()
            if pregunta.show() == Gtk.ResponseType.NO:
                return
            self.actualizar_widgets_revista()
        self.set_widget_revista_como_editables(False)
        self.fecha_revista.definir_estado(self.app_state.revista_seleccionada.estado)


    def bt_agregar_nota_en_revista_clicked(self, widget):
        pass
        # window_nota = DialogNotas(self.app_state)
        # window_nota.set_transient_for(self)
        # window_nota.set_modal(True)
        # # Conectar señal de cierre
        # window_nota.connect("destroy", self.on_nota_window_destroy)
        # window_nota.show_all()

    def bt_cartas_en_revista_clicked(self, widget):
        window_correo = DialogCorreo(self.app_state)
        window_correo.set_transient_for(self)
        window_correo.set_modal(True)
        # Conectar señal de cierre
        window_correo.connect("destroy", self.on_correo_window_destroy)
        window_correo.show_all()


    def ent_buscar_id_activate(self, widget):
        nota_id = self.ent_buscar_nota_por_id_en_revista.get_text()
        if not re.match(config.PATTERN_BUSCAR_ID, nota_id):
            mensaje = MsgBoxInfo("El valor ingresado tiene un formato incorrecto")
            mensaje.show()
            self.ent_buscar_nota_por_id_en_revista.set_text("")
            return
        self.go_to_nota(nota_id)
        self.ent_buscar_nota_por_id_en_revista.set_text("")

    def sb_numero_revista_valuechanged(self, widget):
        self.app_state.sb_numero_revista_signal_activo = True
        if not self.app_state.sb_numero_revista_actualizado_desde_sistema:
            id_revista = int(self.sb_numero_revista.get_value())
            self.actualizar_revista(id_revista)
        self.app_state.sb_numero_revista_signal_activo = False

    def sb_hexagrama_valuechanged(self, widget):
        pass

    def vn_revista_row_activate(self, widget, path, column):
        model = self.vn_revista.tn.get_model()
        i = model.get_iter(path)

        if model.iter_parent(i):
            id_child = model.get_value(i, 11)
            archivo_resumen = ServicesArchivoResumen.get_archivo_resumen_listo(id_child)
            self.run_text_editor_in_window(archivo_resumen)
        else:
            id_nota = model.get_value(i, 0)
            print(f"se hizo click en la nota {id_nota}")

    def on_new_archivo_resumen(self, widget, id_nota):
        if widget == self.vn_revista:
            self.run_text_editor_in_window(nota_id=id_nota, desde="revista")
        elif widget == self.vn_autor:
            self.run_text_editor_in_window(nota_id=id_nota, desde="autores")
        elif widget == self.vn_temas:
            self.run_text_editor_in_window(nota_id=id_nota, desde="temas")
        elif widget == self.vc_analisis:
            self.run_text_editor_in_window(nota_id=id_nota, desde="analisis", tipo="carta")
        elif widget == self.vn_analisis:
            self.run_text_editor_in_window(nota_id=id_nota, desde="analisis")


    def eventbox_im_tapa_clicked(self, widget, event):
        id_revista = self.app_state.revista_seleccionada.id
        fecha = self.app_state.revista_seleccionada.fecha
        mes = utils.formato_fecha(fecha, "mes")
        ano = utils.formato_fecha(fecha, "año")
        if id_revista < 10:
            ruta = f"{ano}/0{id_revista}_El porteño - {mes} {ano[2:]}.pdf"
        else:
            ruta = f"{ano}/{id_revista}_El porteño - {mes} {ano[2:]}.pdf"
        ruta = os.path.abspath(ruta)
        if os.path.exists(ruta):
            wb.open_new(ruta)


    def bt_staff_clicked(self, widget):
        pass

    #Page Autores (P2)

    def ent_buscar_autor_changed(self, widget):
        texto_busqueda = self.ent_buscar_autor.get_text()
        self.actualizar_lista_autores(texto_busqueda)

    def list_autores_row_activate(self, widget, path, column):
        model = self.list_autores.get_model()
        i = model.get_iter(path)
        if not i:
            return
        id_autor = model.get_value(i, 0)
        autor = Autor(AutorServices.get_autor_por_id_autor(id_autor))
        self.actualizar_autor(autor)

    def vn_autor_row_activate(self, widget,path, column):
        model = self.vn_autor.tn.get_model()
        i = model.get_iter(path)

        if not i:
            return

        if model.iter_parent(i):
            id_child = model.get_value(i, 11)
            archivo_resumen = ServicesArchivoResumen.get_archivo_resumen_listo(id_child)
            self.run_text_editor_in_window(archivo_resumen, desde="autores")
        else:
            id_nota =model.get_value(i,0)
            self.go_to_nota(id_nota)
            self.notebook.set_current_page(0)


    def bt_editar_autor_clicked(self, widget):
        self.set_widgets_autores_como_editables(True)

    def bt_guardar_autor_clicked(self, widget):
        data_original = self.get_data_from_app_state_autor()
        data_widgets = self.get_data_from_widgets_autores()
        id_autor = self.app_state.autor_seleccionado.id
        if not utils.changes_were_made(data_original, data_widgets):
            self.set_widgets_autores_como_editables(False)
        else:
            AutorServices.guardar_cambios_autor(id_autor, data_widgets)
            self.set_widgets_autores_como_editables(False)
            self.ent_buscar_autor.set_text("")
            self.seleccionar_autor_en_lista_autores(id_autor)

    def bt_descartar_cambios_en_autor_clicked(self, widget):
        data_original = self.get_data_from_app_state_autor()
        data_widgets = self.get_data_from_widgets_autores()
        if utils.changes_were_made(data_original, data_widgets):
            pregunta = MsgBoxSiNo()
            if pregunta.show() == Gtk.ResponseType.NO:
                return
            self.actualizar_widgets_autor()
        self.set_widgets_autores_como_editables(False)

    # Page tema (P3)

    def ent_buscar_tema_changed(self, widget):
        if not self.app_state.borrar_text_busqueda_temas_sin_actualizar:
            busqueda = self.ent_buscar_tema.get_text()
            self.actualizar_lista_temas(busqueda)

    def list_temas_row_activated(self, widget, path, column):
        model = self.list_temas.get_model()
        i = model.get_iter(path)
        if not i:
            return
        tema = Tema({'id': model.get_value(i, 0), 'tema': model.get_value(i,1)})

        self.fb_temas_seleccionados.agregar_tag(tema)
        self.cargar_notas_en_visor_nota_temas()

        self.app_state.borrar_text_busqueda_temas_sin_actualizar = True
        self.ent_buscar_tema.set_text("")
        self.app_state.borrar_text_busqueda_temas_sin_actualizar = False
        self.actualizar_lista_temas()




    def fb_temas_on_tag_removed(self, widget, tags_selected):
        self.cargar_notas_en_visor_nota_temas()
        self.actualizar_lista_temas()

    def vn_temas_row_activated(self, widget, path, column):
        model = self.vn_temas.tn.get_model()
        i = model.get_iter(path)
        if not i:
            return

        if model.iter_parent(i):
            id_child = model.get_value(i, 11)
            archivo_resumen = ServicesArchivoResumen.get_archivo_resumen_listo(id_child)
            self.run_text_editor_in_window(archivo_resumen, desde="temas")
        else:
            id_nota = model.get_value(i, 0)
            self.go_to_nota(id_nota)
            self.notebook.set_current_page(0)

    # Page Análisis (P4)

    def ent_agregar_grupo_analisis_activate (self, widget):
        text = widget.get_text()
        widget.set_text("")
        if not text:
            return
        pregunta = MsgBoxSiNo("Agregar_grupo")
        if pregunta.show() == Gtk.ResponseType.NO:
            return
        AnalisisService.agregar_grupo_analisis(text)
        self.actualizar_fb_grupos_analisis()
        self.cargar_cb_con_cambio_en_botones()



    def bt_crear_grupo_analisis_clicked(self, widget):
        self.ent_agregar_grupo_analisis_activate(self.ent_agregar_grupo_analisis) # <--- Reenvia al activate del Entry asociado al boton

    def fb_grupos_on_tag_selected(self, widget, selected_tag):
        if not selected_tag:
            self.vn_analisis.borrar_contenido()
            self.lb_titulo_grupos_de_analisis.set_markup("<big><b>Agrupamiento de notas para el análisis:</b></big>")
            self.vc_analisis.borrar_contenido()
            self.lb_titulo_cartas_grupos_de_analisis.set_markup("<big><b>Agrupamiento de cartas de lectores para el análisis:</b></big>")
        else:
            self.actualizar_notas_analisis(selected_tag.id)
            n_filas = len(self.vn_analisis.tn.get_model())
            self.lb_titulo_grupos_de_analisis.set_markup(f"<big><b>Notas para el grupo de análisis <i>{selected_tag.categoria}</i> (n= {n_filas} notas): </b></big>")

            self.vc_analisis.actualizar(selected_tag.id)
            n_filas = len(self.vc_analisis.tc.get_model())
            self.lb_titulo_cartas_grupos_de_analisis.set_markup(f"<big><b>Cartas para el grupo de análisis <i>{selected_tag.categoria}</i> (n= {n_filas} notas): </b></big>")

        if selected_tag:
            ls = self.cb_grupo_analisis.get_model()
            for i, row in enumerate(ls):
                if row[0] == selected_tag.id: self.cb_grupo_analisis.set_active(i)
        else:
            self.cb_grupo_analisis.set_active(-1)

    def ent_id_analisis_activate(self, widget):
        nota_id = widget.get_text()
        if not re.match(config.PATTERN_BUSCAR_ID, nota_id):
            mensaje = MsgBoxInfo("El valor ingresado tiene un formato incorrecto")
            mensaje.show()
            self.ent_buscar_nota_por_id_en_revista.set_text("")
            return

        nota = NotaServices.get_nota_por_id_nota(nota_id)

        if nota:
            nota = Nota(nota)
            self.app_state.nota_a_cargar_en_grupo_analisis = nota
            self.ent_id_analisis.set_text("")
            self.set_widgets_analisis_como_editables(True)
            self.up_label_nota_a_cargar_en_grupo_analisis(nota.titulo)
        else:
            mensaje = MsgBoxInfo("El id no fue encontrado")
            mensaje.show()
            self.app_state.nota_a_cargar_en_grupo_analisis = None
            self.up_label_nota_a_cargar_en_grupo_analisis()
            self.set_widgets_analisis_como_editables(False)

    def bt_cargar_id_analisis_clicked(self, widget):
        self.ent_id_analisis_activate(self.ent_id_analisis)

    def bt_x_carga_id_clicked(self, widget):
        self.resetear_carga_nota_en_grupo_analisis()

    def bt_agrupar_nota_analisis_clicked(self, widget):

        if self.app_state.nota_a_cargar_en_grupo_analisis:
            row = self.cb_grupo_analisis.get_active()
            grupo_id = self.cb_grupo_analisis.get_model()[row][0]
            nota_id = self.app_state.nota_a_cargar_en_grupo_analisis.id

            if AnalisisService.comprobar_si_nota_ya_existe_en_grupo_analisis(nota_id, grupo_id):
                mensaje = MsgBoxInfo("La nota ya ha sido ingresada a este grupo de análisis")
                mensaje.show()
                self.resetear_carga_nota_en_grupo_analisis()
                return
            else:
                AnalisisService.cargar_nota_en_grupo_de_analisis(nota_id, grupo_id)
                self.resetear_carga_nota_en_grupo_analisis()
                self.fb_grupos.activar_boton(grupo_id)
                self.vn_analisis.seleccionar_nota_segun_id(nota_id)

    def vn_analisis_row_activate(self, widget, path, column):
        model = widget.get_model()
        i = model.get_iter(path)
        if not i:
            return
        if model.iter_parent(i):
            id_child = model.get_value(i, 11)
            archivo_resumen = ServicesArchivoResumen.get_archivo_resumen_listo(id_child)
            self.run_text_editor_in_window(archivo_resumen, desde="analisis")
        else:
            id_nota = model.get_value(i, 0)
            self.go_to_nota(id_nota)
            self.notebook.set_current_page(0)

    def vn_analisis_key_press_event(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "Delete":

            grupo = self.fb_grupos.get_selected_tag()

            seleccion = self.vn_analisis.tn.get_selection()
            model, iter = seleccion.get_selected_rows()
            nota_id = model[iter][0]

            AnalisisService.quitar_nota_de_grupo_de_analisis(nota_id, grupo.id)
            self.fb_grupos.activar_boton(grupo.id)

    def vc_analisis_row_activate(self, widget, path, column):

        model = widget.get_model()
        i = model.get_iter(path)
        if not i:
            return

        if model.iter_parent(i):
            id_child = model.get_value(i, 6)
            archivo_resumen = ServicesArchivoResumen.get_archivo_resumen_carta_listo(id_child)
            self.run_text_editor_in_window(archivo_resumen, desde="analisis", tipo="carta")


    def on_editor_window_destroy(self, window, editor, desde, tipo):
        editor.guardar_resumen()

        if desde == "revista":
            self.actualizar_revista(self.app_state.revista_seleccionada.id)
        elif desde == "autores":
            self.actualizar_widgets_autor()
        elif desde == "temas":
            self.cargar_notas_en_visor_nota_temas()
        elif desde == "analisis":
            tag_id = self.fb_grupos.selected_tag.id
            if tipo == "nota":
                self.actualizar_notas_analisis(tag_id)
            else:
                self.vc_analisis.actualizar(tag_id)
        else:
            logger.error(f"No se pudo actualizar el VisualizadorDeNotas porque parámetro desde = {desde} no está identificado")

    def on_correo_window_destroy(self, window):
        pass

    def on_nota_window_destroy(self, window):
        pass

    # FINALIZAR

    def on_destroy(self, widget):
        pass
