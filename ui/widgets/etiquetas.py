from gi.repository import Gtk, GObject #type: ignore
from models import Tema, Categoria

class Etiquetas(Gtk.Box, GObject.GObject):

    __gsignals__ = {
        'button-removed': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.tags = []

        # Configurar el contenedor principal
        self.set_border_width(2)

        # Crear FlowBox con configuración para múltiples elementos por línea
        self.flow_box = Gtk.FlowBox()
        self.flow_box.set_max_children_per_line(10)
        self.flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow_box.set_homogeneous(False)
        self.flow_box.set_hexpand(True)
        self.flow_box.set_margin_top(2)
        self.flow_box.set_margin_bottom(2)
        self.flow_box.set_margin_start(2)
        self.flow_box.set_margin_end(2)

        self.flow_box.set_row_spacing(0)
        self.flow_box.set_column_spacing(0)

        # Crear ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(150) # Altura mínima
        scrolled.set_min_content_width(1200) # Ancho mínima
        scrolled.set_hexpand(True)
        scrolled.add(self.flow_box)
        self.pack_start(scrolled, True, True, 0)


        # # Conectar señal para detectar selecciones
        # self.flow_box.connect("child-activated", self._on_tag_selected)

    def agregar_tag(self, tema: Tema):

        self.tags.append(tema)
        # Crear botones para cada etiqueta
        button = self._create_tag_button(tema.tema)
        self.flow_box.add(button)
        button.show()
        button.set_active(True)

    def _create_tag_button(self, tag: str):
        """Añade un botón de etiqueta compacto al FlowBox"""
        button = Gtk.ToggleButton(label=tag)
        button.set_relief(Gtk.ReliefStyle.NONE)

        button.set_property("can-focus", False)
        button.set_halign(Gtk.Align.START)
        button.set_valign(Gtk.Align.CENTER)

        # Conectar la señal de toggled directamente al botón
        button.connect("toggled", self._on_button_toggled)

        # Aplicar estilo CSS
        button.get_style_context().add_class("tag-button")

        return button


    def _on_button_toggled(self, button):
        """Maneja la selección/deselección de etiquetas"""
        tema_label = button.get_label()
        # hijos = self.flow_box.get_children()

        if not button.get_active():
            for tema in self.tags:
                if tema_label == tema.tema:
                    self.tags.remove(tema)
                    self.flow_box.remove(button)
                    self.emit("button-removed", self.tags)


    def _clear(self):
        hijos = self.flow_box.get_children()
        for hijo in hijos:
            self.flow_box.remove(hijo)

    def get_selected_tags(self):
        """Devuelve la lista de etiquetas seleccionadas"""
        return self.tags.copy()

    def clear_selection(self):
        """Deselecciona todas las etiquetas"""
        for child in self.flow_box.get_children():
            button = child.get_child()
            button.set_active(False)
        self.tags.clear()


class EtiquetasGrupos(Gtk.Box, GObject.GObject):

    __gsignals__ = {
        'tags-changed': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.tags = []
        self.selected_tag = None

        # Configurar el contenedor principal
        self.set_border_width(2)

        # Crear FlowBox con configuración para múltiples elementos por línea
        self.flow_box = Gtk.FlowBox()
        self.flow_box.set_max_children_per_line(1)
        self.flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow_box.set_homogeneous(True)

        self.flow_box.set_row_spacing(0)
        self.flow_box.set_column_spacing(0)

        # Crear ScrolledWindow
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(50) # Altura mínima
        scrolled.set_min_content_width(400) # Ancho mínima
        scrolled.add(self.flow_box)
        self.pack_start(scrolled, False, False, 0)


        # Crear botones para cada etiqueta


        # # Conectar señal para detectar selecciones
        #self.flow_box.connect("child-activated", self._on_tag_selected)

    def cargar_botones(self, grupos: list[Categoria]):
        self._clear()
        for grupo in grupos:
            self.tags.append(grupo)
            button = self._create_tag_button(grupo.categoria)
            self.flow_box.add(button)
            button.show()

    def get_botones(self):
        return self.tags.copy()


    def _create_tag_button(self, tag):
        """Añade un botón de etiqueta compacto al FlowBox"""
        button = Gtk.ToggleButton(label=tag)
        button.set_relief(Gtk.ReliefStyle.NONE)

        button.set_property("can-focus", False)
        button.set_halign(Gtk.Align.FILL)
        button.set_valign(Gtk.Align.CENTER)

        # Conectar la señal de toggled directamente al botón
        button.connect("toggled", self._on_button_toggled)

        # Aplicar estilo CSS
        button.get_style_context().add_class("tag-button2")

        return button


    def _on_button_toggled(self, button):
        """Maneja la selección/deselección de etiquetas"""

        if not button.get_active(): #Sale si el boton se desactiva
            self.selected_tag = None
            self.emit("tags-changed", self.selected_tag)
            return

        # 1. Bloquear la señal de todos los botones para evitar la recursividad
        hijos = self.flow_box.get_children()
        for hijo in hijos:
            child_button = hijo.get_child()
            GObject.signal_handlers_block_matched(child_button, GObject.SignalMatchType.FUNC, 0, 0,
                                                  self._on_button_toggled, None, None)

        # 2. Desactivar todos los botones excepto el que se acaba de activar
        for hijo in hijos:
            child_button = hijo.get_child()
            if child_button != button:
                child_button.set_active(False)

        # 3. Desbloquear las señales
        for hijo in hijos:
            child_button = hijo.get_child()
            GObject.signal_handlers_unblock_matched(child_button, GObject.SignalMatchType.FUNC, 0, 0,
                                                        self._on_button_toggled, None, None)
        tag = button.get_label()
        self.selected_tag = None
        if button.get_active():
            for grupo in self.tags:
                if tag == grupo.categoria:
                    self.selected_tag = grupo

        self.emit("tags-changed", self.selected_tag)

    def get_selected_tag(self):
        """Devuelve la lista de etiquetas seleccionadas"""
        return self.selected_tag

    def clear_selection(self):
        """Deselecciona todas las etiquetas"""
        for child in self.flow_box.get_children():
            button = child.get_child()
            button.set_active(False)
        self.selected_tags.clear()

    def _clear(self):
        self.tags.clear()
        hijos = self.flow_box.get_children()
        for hijo in hijos:
            self.flow_box.remove(hijo)

    def activar_boton(self, grupo_id: int):

        label = None
        self.selected_tag = None

        for tag in self.tags:
            if tag.id == grupo_id:
                label = tag.categoria
                self.selected_tag = tag

        hijos = self.flow_box.get_children()

        # 1. Desactiva las señales
        for hijo in hijos:
            child_button = hijo.get_child()
            GObject.signal_handlers_block_matched(child_button, GObject.SignalMatchType.FUNC, 0, 0,
                                                  self._on_button_toggled, None, None)

        # 2. Setear botones
        for hijo in hijos:
            child_button = hijo.get_child()
            if child_button.get_label() == label:
                child_button.set_active(True)
            else:
                child_button.set_active(False)

        # 3. Desbloquear las señales
        for hijo in hijos:
            child_button = hijo.get_child()
            GObject.signal_handlers_unblock_matched(child_button, GObject.SignalMatchType.FUNC, 0, 0,
                                                        self._on_button_toggled, None, None)

        self.emit("tags-changed", self.selected_tag)