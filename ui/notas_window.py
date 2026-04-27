#ui/notas_window.py
from traceback import print_exception

from gi.repository import Gtk, Gdk, GdkPixbuf
from ui.widgets import LabelNota, EntradaComentarios, ListaMulti
from application_state import EstadoDeAplicacion
import logging

class DialogNotas(Gtk.Window):

    def __init__(self, app_state: EstadoDeAplicacion):
        Gtk.Window.__init__(self, title=f"Notas del numero {app_state.revista_seleccionada.id}")
        self.set_border_width(10)
        self.app_state = app_state
        self._setup_ui()
        self._connect_signals()
        self._iniciar()

    def _setup_ui(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.add(grid)

        #BOTONER Y BARRA SUPERIOR
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = f"Notas del numero {self.app_state.revista_seleccionada.id}"

        self.set_titlebar(header_bar)
        box_bar_for_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_bar_for_buttons.get_style_context(), "linked")

        #izq
        self.bt_bar_anterior = Gtk.Button()
        self.bt_bar_anterior.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT, shadow_type=Gtk.ShadowType.OUT))
        box_bar_for_buttons.add(self.bt_bar_anterior)

        self.bt_bar_posterior = Gtk.Button()
        self.bt_bar_posterior.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT, shadow_type=Gtk.ShadowType.OUT))
        box_bar_for_buttons.add(self.bt_bar_posterior)

        header_bar.pack_start(box_bar_for_buttons)

        #Botones

        self.bt_agregar_nota = Gtk.Button(label="Agregar")
        self.bt_seguir_agregando_nota = Gtk.Button(label="Seguir agregando")
        self.bt_editar = Gtk.Button(label="Editar")
        self.bt_guardar = Gtk.Button(label="Guardar")
        self.bt_descartar = Gtk.Button(label="Descartar")
        self.bt_salir = Gtk.Button(label="Salir")

        #Labels
        self.lb_nota = LabelNota()
        lb_titulo = Gtk.Label(label="Título:")
        lb_seccion = Gtk.Label(label="Sección:")
        lb_dossier = Gtk.Label(label="Dossier:")
        lb_tipo = Gtk.Label(label="Tipo:")
        lb_paginas = Gtk.Label(label="Páginas:")
        lb_autores = Gtk.Label(label="Autorxs:")
        lb_temas = Gtk.Label(label="Temas:")
        lb_comentarios = Gtk.Label(label="Comentarios:")

        #entries
        self.ent_titulo = Gtk.Entry()
        self.ent_seccion = Gtk.Entry()
        self.ent_dossier = Gtk.Entry()
        self.ent_tipo = Gtk.Entry()
        self.ent_paginas = Gtk.Entry()
        self.txt_comentario = EntradaComentarios()
        self.txt_comentario.scroll.set_vexpand(True)

        #Autores y temas
        self.lista_autores = ListaMulti()
        self.lista_temas = ListaMulti()


        #Grid

        grid.attach(self.bt_agregar_nota, 0,0,1,1)
        grid.attach(self.lb_nota, 1,0,4,1)
        grid.attach(self.bt_seguir_agregando_nota, 0,1,1,1)
        grid.attach(lb_titulo, 1,1,1,1)
        grid.attach(self.ent_titulo, 2,1,3,1)
        grid.attach(self.bt_editar, 0,2,1,1)
        grid.attach(lb_seccion,1,2,1,1)
        grid.attach(self.ent_seccion,2,2,1,1)
        grid.attach(lb_dossier, 3, 2, 1, 1)
        grid.attach(self.ent_dossier,4,2,1,1)
        grid.attach(self.bt_guardar, 0,3,1,1)
        grid.attach(lb_tipo, 1, 3, 1, 1)
        grid.attach(self.ent_tipo,2,3,1,1)
        grid.attach(lb_paginas, 3,3,1,1)
        grid.attach(self.ent_paginas, 4,3,1,1)
        grid.attach(self.bt_descartar, 0,4,1,1)
        grid.attach(lb_autores, 1,4,1,1)
        grid.attach(self.lista_autores, 2,4,3,3)
        grid.attach(lb_temas, 1,7,1,1)
        grid.attach(self.lista_temas, 2,7,3,3)
        grid.attach(self.bt_salir, 0,5,1,1)
        grid.attach(lb_comentarios,1,10,1,1)
        grid.attach(self.txt_comentario.empaquetar(), 1,11,4,4)



    def _connect_signals(self):
        pass

    def _iniciar(self):
         if self.app_state.nota_seleccionada:
            self.habilitar_edicion(False)


    def habilitar_edicion(self, editable: bool):
        if editable:
            self.app_state.nota_edicion_activa = True
            #botones         
            self.bt_agregar_nota.set_sensitive(False)
            self.bt_seguir_agregando_nota.set_sensitive(True)
            self.bt_editar.set_sensitive(False)
            self.bt_guardar.set_sensitive(True)
            self.bt_descartar.set_sensitive(True)
            #campos
            self.ent_titulo.set_editable(True)
            self.ent_seccion.set_editable(True)
            self.ent_dossier.set_editable(True)
            self.ent_tipo.set_editable(True)
            self.ent_paginas.set_editable(True)
            self.lista_autores.set_editable(True)
            self.txt_comentario.set_editable(True)
        else:
            #botones         
            self.app_state.nota_edicion_activa = False         
            self.bt_agregar_nota.set_sensitive(True)
            self.bt_seguir_agregando_nota.set_sensitive(False)
            self.bt_editar.set_sensitive(True)
            self.bt_guardar.set_sensitive(False)
            self.bt_descartar.set_sensitive(False)
            #campos
            self.ent_titulo.set_editable(False)
            self.ent_seccion.set_editable(False)
            self.ent_dossier.set_editable(False)
            self.ent_tipo.set_editable(False)
            self.ent_paginas.set_editable(False)
            self.lista_autores.set_editable(False)
            self.txt_comentario.set_editable(False)
        self.configurar_headers()

    def configurar_headers(self):
        
        notas = self.app_state.revista_seleccionada.notas

        if self.app_state.nota_edicion_activa:
            if notas and not self.is_first():
                self.bt_bar_anterior.set_sensitive(True)
            else:
                self.bt_bar_anterior.set_sensitive(False)
            self.bt_bar_posterior.set_sensitive(False)
        else:
            if self.is_first():
                self.bt_bar_anterior.set_sensitive(False)
            self.bt_bar_posterior.set_sensitive(True)

    def is_last(self): #Chequea si la nota seleccionada es la última cargada para esa revista
        if self.app_state.revista_seleccionada.notas:
            if self.app_state.nota_seleccionada.id == self.app_state.revista_seleccionada.notas[-1].id:
                return True
        return False

    def is_first(self): #Chequea si la nota seleccionda es la primera cargada para esa revista
        if self.app_state.revista_seleccionada.notas:
            if self.app_state.nota_seleccionada.id == self.app_state.revista_seleccionada.notas[0].id:
                return True
        return False
