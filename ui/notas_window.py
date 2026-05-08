#ui/notas_window.py
from traceback import print_exception

from gi.repository import Gtk # type: ignore
from ui.widgets import LabelNota, EntradaComentarios, MsgSiNo
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
        self._fun_actualizar_nota_en_main = fun_actualizar_nota
        self._nota_new:bool = False
        self._edicion_activa: bool = False

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
        self.bt_bar_anterior.connect("clicked", self._bt_bar_anterior_clicked) #P1-Botón Editar_Click
        self.bt_bar_posterior.connect("clicked", self._bt_bar_posterior_clicked) #P1 - Botón Guardar_Click
        self.bt_editar.connect("clicked", self._bt_editar_clicked)
        self.bt_descartar.connect("clicked", self._bt_descartar_clicked)
        self.bt_salir.connect("clicked", self._bt_salir_clicked)


    def _iniciar(self):
        if self.app_state.nota_seleccionada:
            self._cargar_nota_en_widgets(self.app_state.nota_seleccionada)
            self._habilitar_edicion(False)
        else:
            self._nota_new = True
            self._habilitar_edicion(True)
            self._widgets_para_nueva_nota()

    def _cargar_nota(self, nota: Nota):
        self._cargar_nota_en_app_state(nota)
        self._cargar_nota_en_widgets(nota)
        self._fun_actualizar_nota_en_main(nota.id)

    def _cargar_nota_en_app_state(self, nota: Nota):
        self.app_state.nota_seleccionada = None
        self.app_state.nota_seleccionada = nota


    def _habilitar_edicion(self, editable: bool):
        if editable:
            self._edicion_activa = True
            #botones         
            self.bt_agregar_nota.set_sensitive(False)
            if self._nota_new:
                self.bt_seguir_agregando_nota.set_sensitive(True)
            else:
                self.bt_seguir_agregando_nota.set_sensitive(False) 
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
            self._set_editable_lista_autores()
            self._set_editable_lista_temas()
            self.txt_comentario.set_editable(True)
            #labels
            self.lb_nota.formato_en_edicion()
        else:
            self._edicion_activa = False
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
        self._configurar_headers()

    def _configurar_headers(self):
        
        notas = self.app_state.revista_seleccionada.notas

        if self._edicion_activa:
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

    def _cargar_nota_en_widgets (self, nota: Nota):
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

    def _clear_widgets(self):
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

    def _widgets_para_nueva_nota(self):
        self._clear_widgets()
        self.lb_nota.formato_nota_nueva()

    def _set_editable_lista_autores(self,):
        self.lista_autores.set_editable(True)
        self._cargar_lista_de_autores_en_lista_multi()

    def _set_editable_lista_temas(self,):
        self.lista_temas.set_editable(True)
        self._cargar_lista_de_temas_en_lista_multi()

    def _cargar_lista_de_autores_en_lista_multi(self):
        lista_aut = AutorServices.get_lista_autores_por_nombre()
        self.lista_autores.cargar_todos_los_elementos(utils.to_autor(lista_aut))

    def _cargar_lista_de_temas_en_lista_multi(self):
        lista_tem = TemaServices.get_temas_busqueda()
        self.lista_temas.cargar_todos_los_elementos(utils.to_tema(lista_tem))

    def _get_data_from_widgets(self) -> dict:
        diccionario = {"id": self.app_state.nota_seleccionada.id,
                       "titulo": self.ent_titulo.get_text(),
                       "paginas": self.ent_paginas.get_text(),
                       "dossier": self.ent_dossier.get_text(),
                       "seccion": self.ent_seccion.get_text(),
                       "tipo": self.ent_tipo.get_text(),
                       "original": self.chb_original.get_active(),
                       "relacionado": self.chb_relacionado.get_active(),
                       "relacionado_sexualidad": self.chb_relacionado_sexualidad.get_active(),
                       "relacionado_memoria": self.chb_relacionado_memoria.get_active(),
                       "comentarios": self.txt_comentario.get_text(),
                       "autores": self.lista_autores.get_selection(),
                       "temas": self.lista_temas.get_selection(),
                       "categorias": self.app_state.nota_seleccionada.categorias,
                       "analisis": self.app_state.nota_seleccionada.analisis}
        return diccionario


    
    #ACTIVAR WIDGETS POR SEÑALES

    def _bt_bar_anterior_clicked(self, widget):
        self._clear_widgets()
        if self._edicion_activa:
            self._habilitar_edicion(False)
        if self._nota_new:
            new_index = len(self.app_state.revista_seleccionada.notas) - 1
            nota = self.app_state.revista_seleccionada.notas[new_index]
            self._nota_new = False
        else:
            new_index = self.app_state.revista_seleccionada.notas.index(self.app_state.nota_seleccionada) - 1
            nota = self.app_state.revista_seleccionada.notas[new_index]

        self._cargar_nota(nota)

        if not new_index:
            widget.set_sensitive(False)

    def _bt_bar_posterior_clicked(self, widget):
        self._clear_widgets()
        if self.is_last():
            self._widgets_para_nueva_nota()
        else:
            new_index = self.app_state.revista_seleccionada.notas.index(self.app_state.nota_seleccionada) + 1
            nota = self.app_state.revista_seleccionada.notas[new_index]
            self._cargar_nota(nota)

        self.bt_bar_anterior.set_sensitive(True)
        
    def _bt_editar_clicked(self, widget):
        self._habilitar_edicion(True)

    def _bt_descartar_clicked(self, widget):

        if self._nota_new:
            self._habilitar_edicion(False)
            self._clear_widgets()
            self._cargar_nota(self.app_state.revista_seleccionada.notas[-1])
        else:
            from_original = self.app_state.nota_seleccionada.to_dict()
            from_widgets = self._get_data_from_widgets()
            if utils.changes_were_made(from_original, from_widgets):
                pregunta = MsgSiNo()
                if pregunta.show() == Gtk.ResponseType.NO:
                    return
            self._habilitar_edicion(False)
            self._clear_widgets()
            self._cargar_nota_en_widgets(self.app_state.nota_seleccionada)

    def _bt_salir_clicked(self, widget):
        self.close()