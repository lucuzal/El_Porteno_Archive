from gi.repository import Gtk, Gdk, GdkPixbuf

import utils
from ui.widgets import EntradaComentarios, MsgBoxSiNo, MsgBoxInfo
from models import Carta, Categoria

from services import CartaServices, AnalisisService, RevistaServices
import logging

logger = logging.getLogger(__name__)

class DialogCorreo(Gtk.Window):

    def __init__(self, app_state):
        self.app_state = app_state
        Gtk.Window.__init__(self, title=f"Correo lector para la revista n° {self.app_state.revista_seleccionada}")
        self.set_border_width(10)
        self.set_default_size(600, 400)

        self._setup_ui()
        self._connect_signals()
        self._iniciar()

    def _setup_ui(self):

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.add(grid)

        # BOTONERA Y BARRA SUPERIOR
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = f"Correo Lector de Rev {self.app_state.revista_seleccionada.id}"

        self.set_titlebar(header_bar)
        box_bar_for_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box_bar_for_buttons.get_style_context(), "linked")

        #izq
        self.bt_bar_anterior = Gtk.Button()
        self.bt_bar_anterior.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.LEFT, shadow_type=Gtk.ShadowType.NONE))
        box_bar_for_buttons.add(self.bt_bar_anterior)

        #der
        self.bt_bar_posterior = Gtk.Button()
        self.bt_bar_posterior.add(Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT, shadow_type=Gtk.ShadowType.OUT))
        box_bar_for_buttons.add(self.bt_bar_posterior)

        header_bar.pack_start(box_bar_for_buttons)

        #widgets principales
        self.lb_cartas = Gtk.Label()
        self.lb_cartas.set_markup("<span size=\"x-large\"><b>CORREO LECTOR X/X</b></span>")
        self.lb_cartas.set_halign(Gtk.Align.CENTER)

        lb_remitente = Gtk.Label(label="Remitente/s:")
        self.ent_remitente = Gtk.Entry()

        self.chb_relevante = Gtk.CheckButton(label="¿es relevante?")

        lb_comentarios = Gtk.Label(label="Descripción:")
        self.ent_comentarios = EntradaComentarios()
        self.ent_comentarios.scroll.set_vexpand(True)

        self.bt_salir = Gtk.Button(label="Salir")
        self.bt_descartar = Gtk.Button(label="Descartar")
        self.bt_guardar = Gtk.Button(label="Guardar")
        self.bt_editar = Gtk.Button(label="Editar")

        lb_categorias = Gtk.Label(label="Cargar en:")
        ls_items = Gtk.ListStore(int, str)
        self.cb_grupo_analisis = Gtk.ComboBox.new_with_model(ls_items)
        rendered_text = Gtk.CellRendererText()
        self.cb_grupo_analisis.pack_start(rendered_text, True)
        self.cb_grupo_analisis.add_attribute(rendered_text, "text", 1)
        self.bt_cargar_grupo_analisis = Gtk.Button(label="--->")
        self.lb_cartas_analisis = Gtk.Label(label="\n La carta no está cargada en ningún grupo de análisis \n")

        #Panel derecho contenedor del editor:
        self.panel_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.panel_container.set_size_request(30, -1)
        Gtk.StyleContext.add_class(self.panel_container.get_style_context(), "sidebar-panel")

        grid.attach(self.lb_cartas, 0,0,4,1)
        grid.attach(lb_remitente, 0,1,1,1)
        grid.attach(self.ent_remitente, 1,1,3,1)
        grid.attach(self.chb_relevante, 1,2,1,1)
        grid.attach(lb_comentarios, 0,3,1,1)
        grid.attach(self.ent_comentarios.empaquetar(),1,3,3,1)
        grid.attach(lb_categorias,0,4,1,1)
        grid.attach(self.cb_grupo_analisis, 1,4,2,1)
        grid.attach(self.bt_cargar_grupo_analisis, 3,4,1,1)
        grid.attach(self.lb_cartas_analisis, 0,5,5,1)
        grid.attach(self.bt_salir, 0,6,1,1)
        grid.attach(self.bt_descartar, 1,6,1,1)
        grid.attach(self.bt_guardar, 2,6,1,1)
        grid.attach(self.bt_editar, 3,6,1,1)


    def _connect_signals(self):
        self.bt_bar_anterior.connect("clicked", self.bt_bar_anterior_clicked)
        self.bt_bar_posterior.connect("clicked", self.bt_bar_posterior_clicked)
        self.bt_salir.connect("clicked", self.bt_salir_clicked)
        self.bt_descartar.connect("clicked", self.bt_descartar_clicked)
        self.bt_editar.connect("clicked", self.bt_editar_clicked)
        self.bt_guardar.connect("clicked", self.bt_guardar_clicked)
        self.bt_cargar_grupo_analisis.connect("clicked", self.bt_cargar_grupo_analisis_clicked)
        self.connect("destroy", self.on_destroy_correo)

    def _iniciar(self):
        n_cartas = len(self.app_state.revista_seleccionada.correo)
        self.actualizar_cb_grupo_analisis()
        if not n_cartas:
            self.set_widgets_para_nueva_carta()
        else:
            carta = self.app_state.revista_seleccionada.correo[0]
            self.cargar_carta(carta)

    def habilitar_edicion(self, edicion: bool):
        if edicion:
            self.app_state.correo_edicion_activa = True
            self.ent_remitente.set_editable(True)
            self.chb_relevante.set_sensitive(True)
            self.ent_comentarios.tv.set_editable(True)
            self.bt_descartar.set_sensitive(True)
            self.bt_guardar.set_sensitive(True)
            self.bt_editar.set_sensitive(False)
            self.cb_grupo_analisis.set_sensitive(False)
            self.bt_cargar_grupo_analisis.set_sensitive(False)
            self.configurar_botones_headbar()
        else:
            self.app_state.correo_edicion_activa = False
            self.ent_remitente.set_editable(False)
            self.ent_comentarios.tv.set_editable(False)
            self.chb_relevante.set_sensitive(False)
            self.bt_descartar.set_sensitive(False)
            self.bt_guardar.set_sensitive(False)
            self.bt_editar.set_sensitive(True)
            self.cb_grupo_analisis.set_sensitive(True)
            self.bt_cargar_grupo_analisis.set_sensitive(True)
            self.configurar_botones_headbar()


    def is_last(self):
        if self.app_state.revista_seleccionada.correo:
            if self.app_state.carta_seleccionada.id == self.app_state.revista_seleccionada.correo[-1].id:
                return True
        return False

    def is_first(self):
        if self.app_state.revista_seleccionada.correo:
            if self.app_state.carta_seleccionada.id == self.app_state.revista_seleccionada.correo[0].id:
                return True
        return False

    def cargar_carta(self, carta: Carta):
        self.cargar_carta_en_app_state(carta)
        self.habilitar_edicion(False)
        self.cargar_carta_en_widgets(carta)

    def cargar_carta_en_app_state(self, carta: Carta = None):
        self.app_state.carta_seleccionada = carta if carta else None

    def cargar_carta_en_widgets(self, carta: Carta):

        self.ent_remitente.set_text(carta.remitente)
        self.chb_relevante.set_active(carta.relevante)
        self.ent_comentarios.set_text(carta.tema)
        self.configurar_label_principal(carta.id)
        self.actualizar_lb_grupo_analisis()

    def get_data_from_carta_app_state(self):

        carta = self.app_state.carta_seleccionada
        dictionary = {'id': carta.id,
                      'revista_id': carta.revista,
                      'remitente':carta.remitente,
                      'tema':carta.tema,
                      'relevante':carta.relevante}
        return dictionary

    def get_data_from_carta_widgets(self):

        dictionary = {'id': self.app_state.carta_seleccionada.id,
                      'revista_id': self.app_state.carta_seleccionada.revista,
                      'remitente': self.ent_remitente.get_text(),
                      'tema': self.ent_comentarios.get_text(),
                      'relevante': self.chb_relevante.get_active()}
        return dictionary



    def clear_widgets(self):
        self.ent_remitente.set_text("")
        self.chb_relevante.set_active(False)
        self.ent_comentarios.set_text("")
        self.configurar_label_principal()
        self.lb_cartas_analisis.set_text("")

    def set_widgets_para_nueva_carta(self):
        self.bt_bar_posterior.set_sensitive(False)
        self.clear_widgets()
        self.habilitar_edicion(True)
        self.app_state.correo_new = True
        self.configurar_label_principal()

    def configurar_botones_headbar(self):

        correo = self.app_state.revista_seleccionada.correo

        if self.app_state.correo_edicion_activa:
            if correo and not self.is_first():
                self.bt_bar_anterior.set_sensitive(True)
            else:
                self.bt_bar_anterior.set_sensitive(False)
            self.bt_bar_posterior.set_sensitive(False)
        else:
            if self.is_first():
                self.bt_bar_anterior.set_sensitive(False)
            self.bt_bar_posterior.set_sensitive(True)

    def configurar_label_principal(self, carta_id: int = None):
        correo = self.app_state.revista_seleccionada.correo
        n_cartas = len(correo)
        indice = 0

        if self.app_state.correo_edicion_activa and self.app_state.correo_new:
            self.lb_cartas.set_markup("<span size=\"x-large\"><b>INGRESAR NUEVA CARTA</b></span>")
        elif self.app_state.correo_edicion_activa and not self.app_state.correo_new:
            indice = correo.index(self.app_state.carta_seleccionada) + 1
            self.lb_cartas.set_markup(f"<span size=\"x-large\"><b>EDITAR CARTA {indice}/{n_cartas}</b></span>")
        else:
            indice = correo.index(self.app_state.carta_seleccionada) + 1
            self.lb_cartas.set_markup(f"<span size=\"x-large\"><b>CORREO LECTOR {indice}/{n_cartas}</b></span>")

    def actualizar_cb_grupo_analisis(self):
        ls = self.cb_grupo_analisis.get_model()
        ls.clear()
        grupos = AnalisisService.get_grupos_analisis()
        for grupo in grupos:
            ls.append([grupo.id, grupo.categoria])

    def are_widgets_empty(self):
        remitente = True if self.ent_remitente.get_text() == "" else False
        relevante = True if not self.chb_relevante.get_active() else False
        tema = True if self.ent_comentarios.get_text() == "" else False

        if remitente and relevante and tema:
            return True
        else:
            return False

    def actualizar_correo(self): #Se encarga de actualizar Correo en la revista desde la base de datos después de hacer modificaciones
        self.app_state.revista_seleccionada.correo.clear()
        RevistaServices.cargar_correo(self.app_state.revista_seleccionada)


    def actualizar_lb_grupo_analisis(self):
        categorias = self.app_state.carta_seleccionada.categoria_analisis
        n_categorias = len(categorias) if categorias else 0
        if n_categorias == 1:
            texto = f"\n La carta pertenece al grupo de análisis {categorias[0].categoria}"
        elif n_categorias == 2:
            texto = f"\n La carta pertenece a los grupos de análisis {categorias[0].categoria} y {categorias[1].categoria}"
        elif n_categorias > 2:
            texto = f"\n La carta pertenece a los grupos de análisis: "
            for i, grupo in enumerate(categorias, 1):
                texto += f" {grupo.categoria}"
                if i + 1 == n_categorias:
                    texto += " y"
        else:
            texto = "\n La carta no está cargada en ningún grupo de análisis"
        texto += "\n"
        self.lb_cartas_analisis.set_text(texto)



    # ACTIVACION DE WIDGETS POR SEÑALES

    def bt_bar_anterior_clicked(self, widget):
        self.clear_widgets()
        if self.app_state.correo_edicion_activa:
            self.habilitar_edicion(False)
        if self.app_state.correo_new:
            new_index = len(self.app_state.revista_seleccionada.correo) - 1
            carta = self.app_state.revista_seleccionada.correo[new_index]
            self.app_state.correo_new = False
        else:
            new_index = self.app_state.revista_seleccionada.correo.index(self.app_state.carta_seleccionada) - 1
            carta = self.app_state.revista_seleccionada.correo[new_index]

        self.cargar_carta(carta)

        if not new_index:
            widget.set_sensitive(False)

    def bt_bar_posterior_clicked(self, widget):
        self.clear_widgets()
        if self.is_last():
            self.set_widgets_para_nueva_carta()
        else:
            new_index = self.app_state.revista_seleccionada.correo.index(self.app_state.carta_seleccionada) + 1
            carta = self.app_state.revista_seleccionada.correo[new_index]
            self.cargar_carta_en_app_state(carta)
            self.cargar_carta_en_widgets(carta)

        self.bt_bar_anterior.set_sensitive(True)


    def bt_salir_clicked(self, widget):
        self.close()

    def bt_descartar_clicked(self, widget):
        if self.app_state.correo_new:
            if not self.app_state.revista_seleccionada.correo:
                self.clear_widgets()
                return
            else:
                self.app_state.correo_new = False
                carta = self.app_state.revista_seleccionada.correo[-1]
                self.cargar_carta(carta)
        else:
            data_original = self.get_data_from_carta_app_state()
            data_actual = self.get_data_from_carta_widgets()

            if utils.changes_were_made(data_original, data_actual):
                pregunta = MsgBoxSiNo
                if pregunta.show() == Gtk.ResponseType.NO:
                    return

            self.habilitar_edicion(False)
            self.cargar_carta_en_widgets(self.app_state.carta_seleccionada)


    def bt_guardar_clicked(self, widget):
        correo = self.app_state.revista_seleccionada.correo
        data_actual = self.get_data_from_carta_widgets()
        data_original = self.get_data_from_carta_app_state()
        if self.app_state.correo_new:
            if self.are_widgets_empty():
                self.app_state.correo_new = False
                self.cargar_carta(correo[-1])
                return
            else:
                CartaServices.guardar_nueva_carta(data_actual, self.app_state.revista_seleccionada.id)
                self.actualizar_correo()
                self.cargar_carta(correo[-1])
        else:
            if utils.changes_were_made(data_original, data_actual):
                CartaServices.actualizar_carta(data_actual)
                self.actualizar_correo()
                for carta in self.app_state.revista_seleccionada.correo:
                    if carta.id == data_actual['id']:
                        self.cargar_carta(carta)
            else:
                self.habilitar_edicion(False)
                return

    def bt_editar_clicked(self, widget):
        self.habilitar_edicion(True)
        self.configurar_label_principal()

    def bt_cargar_grupo_analisis_clicked(self, widget):
        model = self.cb_grupo_analisis.get_model()
        row = self.cb_grupo_analisis.get_active()
        carta_id = self.app_state.carta_seleccionada.id

        if row == -1:
            msg = MsgBoxInfo("Seleccione un grupo para ingresar")
            msg.show()
            return

        valor = model[row] if row != -1 else None
        grupo_analisis = Categoria({'id': valor[0], 'grupo': valor[1]})

        if grupo_analisis in self.app_state.carta_seleccionada.categoria_analisis:
            msg = MsgBoxInfo("La carta ya está ingresada al grupo análisis")
            msg.show()
            return

        CartaServices.agregar_carta_a_grupo_de_analisis(carta_id, grupo_analisis.id)
        self.actualizar_correo()
        for carta in self.app_state.revista_seleccionada.correo:
            if carta.id == carta_id:
                self.cargar_carta(carta)

    def on_destroy_correo(self, widget):
        pass








