#ui/notas_window.py
from traceback import print_exception

from gi.repository import Gtk, Gdk, GdkPixbuf # type: ignore
from ui.widgets import LabelNota, EntradaComentarios
from ui.widgets.lista_multi import ListaMulti
from application_state import EstadoDeAplicacion
from models import Nota
from services import AutorServices, TemaServices
import utils

class DialogNotas(Gtk.Window):

    def __init__(self, app_state: EstadoDeAplicacion, fun_actualizar_nota):
        Gtk.Window.__init__(self, title=f"Notas del numero {app_state.revista_seleccionada.id}")
        self.set_border_width(10)
        self.app_state = app_state
        self._fun_actualizar_nota = fun_actualizar_nota
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

        #checks buttons
        self.chb_original = Gtk.CheckButton(label="¿es original?")
        self.chb_relacionado = Gtk.CheckButton(label="¿es relevante?")
        self.chb_relacionado_memoria = Gtk.CheckButton(label="con memoria")
        self.chb_relacionado_sexualidad = Gtk.CheckButton(label="con sexualidad")
        box_relevante = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_relevante.pack_start(self.chb_original, True, True, 0)
        box_relevante.pack_start(self.chb_relacionado, True, True, 0)
        box_relevante.pack_start(self.chb_relacionado_memoria, True, True, 0)
        box_relevante.pack_start(self.chb_relacionado_sexualidad, True, True, 0)

        #Autores y temas
        self.lista_autores = ListaMulti(es_autor=True)
        self.lista_temas = ListaMulti(es_autor=False)


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
        grid.attach(box_relevante, 2,4,3,1)
        grid.attach(lb_autores, 1,5,1,1)
        grid.attach(self.lista_autores, 2,5,3,3)
        grid.attach(lb_temas, 1,8,1,1)
        grid.attach(self.lista_temas, 2,8,3,3)
        grid.attach(self.bt_salir, 0,5,1,1)
        grid.attach(lb_comentarios,1,11,1,1)
        grid.attach(self.txt_comentario.empaquetar(), 1,12,4,4)



    def _connect_signals(self):
        self.bt_bar_anterior.connect("clicked", self.bt_bar_anterior_clicked) #P1-Botón Editar_Click
        self.bt_bar_posterior.connect("clicked", self.bt_bar_posterior_clicked) #P1 - Botón Guardar_Click
        self.bt_editar.connect("clicked", self.bt_editar_clicked)


    def _iniciar(self):
        if self.app_state.nota_seleccionada:
            self.cargar_nota_en_widgets(self.app_state.nota_seleccionada)
            self.habilitar_edicion(False)
        else:
            self.app_state.nota_new = True
            self.habilitar_edicion(True)
            self.widgets_para_nueva_nota()

    def cargar_nota(self, nota: Nota):
        self.cargar_nota_en_app_state(nota)
        self.cargar_nota_en_widgets(nota)
        self._fun_actualizar_nota(nota.id)

    def cargar_nota_en_app_state(self, nota: Nota):
        self.app_state.nota_seleccionada = None
        self.app_state.nota_seleccionada = nota


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
            self.chb_original.set_sensitive(True)
            self.chb_relacionado.set_sensitive(True)
            self.chb_relacionado_memoria.set_sensitive(True)
            self.chb_relacionado_sexualidad.set_sensitive(True)
            self.set_editable_lista_autores()
            self.set_editable_lista_temas()
            self.txt_comentario.set_editable(True)
            #labels
            self.lb_nota.formato_en_edicion()
        else:
            self.app_state.nota_edicion_activa = False
            #botones                  
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
            self.chb_original.set_sensitive(False)
            self.chb_relacionado.set_sensitive(False)
            self.chb_relacionado_memoria.set_sensitive(False)
            self.chb_relacionado_sexualidad.set_sensitive(False)
            self.lista_autores.set_editable(False)
            self.lista_temas.set_editable(False)
            self.txt_comentario.set_editable(False)
            #labels
            self.lb_nota.formato_visualizacion()
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
        if self.app_state.revista_seleccionada.notas and self.app_state.nota_seleccionada:
            if self.app_state.nota_seleccionada.id == self.app_state.revista_seleccionada.notas[0].id:
                return True
        return False

    def cargar_nota_en_widgets (self, nota: Nota):
        self.ent_titulo.set_text(nota.titulo)
        self.ent_seccion.set_text(nota.seccion)
        self.ent_dossier.set_text(nota.dossier)
        self.ent_tipo.set_text(nota.tipo)
        self.ent_paginas.set_text(nota.paginas)
        self.chb_original.set_active(nota.original)
        self.chb_relacionado.set_active(nota.relacionado)
        self.chb_relacionado_memoria.set_active(nota.relacionado_memoria)
        self.chb_relacionado_sexualidad.set_active(nota.relacionado_sexualidad)
        self.lista_autores.set_elementos_seleccionados_full(nota.autores)
        self.lista_temas.set_elementos_seleccionados_full(nota.temas)
        self.txt_comentario.set_text(nota.comentarios)
        self.lb_nota.actualizar_nota(nota.id)

    def clear_widgets(self):
        self.ent_titulo.set_text("")
        self.ent_seccion.set_text("")
        self.ent_dossier.set_text("")
        self.ent_tipo.set_text("")
        self.ent_paginas.set_text("")
        self.chb_original.set_active(False)
        self.chb_relacionado.set_active(False)
        self.chb_relacionado_memoria.set_active(False)
        self.chb_relacionado_sexualidad.set_active(False)
        self.lista_autores.clear()
        self.lista_temas.clear()
        self.txt_comentario.borrar_contenido()

    def widgets_para_nueva_nota(self):
        self.clear_widgets()
        self.lb_nota.formato_nota_nueva()

    def set_editable_lista_autores(self,):
        self.lista_autores.set_editable(True)
        self.cargar_lista_de_autores_en_lista_multi()

    def set_editable_lista_temas(self,):
        self.lista_temas.set_editable(True)
        self.cargar_lista_de_temas_en_lista_multi()

    def cargar_lista_de_autores_en_lista_multi(self):
        lista_aut = AutorServices.get_lista_autores_por_nombre()
        self.lista_autores.cargar_todos_los_elementos(utils.to_autor(lista_aut))

    def cargar_lista_de_temas_en_lista_multi(self):
        lista_tem = TemaServices.get_temas_busqueda()
        self.lista_temas.cargar_todos_los_elementos(utils.to_tema(lista_tem))


    
    #ACTIVAR WIDGETS POR SEÑALES

    def bt_bar_anterior_clicked(self, widget):
        self.clear_widgets()
        if self.app_state.nota_edicion_activa:
            self.habilitar_edicion(False)
        if self.app_state.nota_new:
            new_index = len(self.app_state.revista_seleccionada.notas) - 1
            nota = self.app_state.revista_seleccionada.notas[new_index]
            self.app_state.nota_new = False
        else:
            new_index = self.app_state.revista_seleccionada.notas.index(self.app_state.nota_seleccionada) - 1
            nota = self.app_state.revista_seleccionada.notas[new_index]

        self.cargar_nota(nota)

        if not new_index:
            widget.set_sensitive(False)

    def bt_bar_posterior_clicked(self, widget):
        self.clear_widgets()
        if self.is_last():
            self.widgets_para_nueva_nota()
        else:
            new_index = self.app_state.revista_seleccionada.notas.index(self.app_state.nota_seleccionada) + 1
            nota = self.app_state.revista_seleccionada.notas[new_index]
            self.cargar_nota(nota)

        self.bt_bar_anterior.set_sensitive(True)
        
    def bt_editar_clicked(self, widget):
        pass

