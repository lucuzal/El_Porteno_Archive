from gi.repository import Gtk, Gdk, Pango #type: ignore
from models import ArchivoResumen
from utils import html_to_buffer, buffer_to_html, press_button
from services import ServicesArchivoResumen
import logging

logger = logging.getLogger(__name__)

class TextEditor(Gtk.Box):
    def __init__(self, tipo: str = "nota"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_border_width(10)

        #Estado del formato =
        self.active_tags = {
            "bold": False,
            "italic": False,
            "color": None
        }

        self.archivo_resumen = None
        self.tipo = tipo

        self.text_buffer = Gtk.TextBuffer.new(None)

        # 2. Configurar los tags de formato
        tag_table = self.text_buffer.get_tag_table()

        # Negritas
        self.tag_bold = Gtk.TextTag.new("bold")
        self.tag_bold.set_property("weight", Pango.Weight.BOLD)
        tag_table.add(self.tag_bold)

        # Cursivas
        self.tag_italic = Gtk.TextTag.new("italic")
        self.tag_italic.set_property("style", Pango.Style.ITALIC)
        tag_table.add(self.tag_italic)

        # Colores de primer plano (fuente)
        self.tag_red = Gtk.TextTag.new("red")
        self.tag_red.set_property("foreground", "#ff6b6b")
        tag_table.add(self.tag_red)

        self.tag_orange = Gtk.TextTag.new("orange")
        self.tag_orange.set_property("foreground", "#ffa500")
        tag_table.add(self.tag_orange)

        self.tag_yellow = Gtk.TextTag.new("yellow")
        self.tag_yellow.set_property("foreground", "#ffd166")
        tag_table.add(self.tag_yellow)

        self.tag_map = {
            "bold": self.tag_bold,
            "italic": self.tag_italic,
            "red":self.tag_red,
            "orange":self.tag_orange,
            "yellow": self.tag_yellow
        }

        self.text_buffer.connect("insert-text", self.on_insert_text)

        self.text_view = Gtk.TextView.new_with_buffer(self.text_buffer)
        self.text_view.connect("key-press-event", self.on_key_press_event)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)



        # 3. Crear botones para las acciones
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_halign(Gtk.Align.CENTER)

        self.btn_bold = Gtk.ToggleButton(label="B")
        self.btn_bold.get_style_context().add_class("tag-button2")
        self.btn_bold.connect("toggled", self.on_toggled_bold)
        toolbar.pack_start(self.btn_bold, False, False, 0)

        self.btn_italic = Gtk.ToggleButton(label="I")
        self.btn_italic.get_style_context().add_class("tag-button2")
        self.btn_italic.connect("toggled", self.on_toggled_italic)
        toolbar.pack_start(self.btn_italic, False, False, 0)

        # Botones de color
        self.btn_red = Gtk.ToggleButton(label="🔴")
        self.btn_red.get_style_context().add_class("tag-button2")
        self.btn_red.connect("toggled", self.on_color_toggled, "red")
        toolbar.pack_start(self.btn_red, False, False, 0)

        self.btn_orange = Gtk.ToggleButton(label="🟠")
        self.btn_orange.get_style_context().add_class("tag-button2")
        self.btn_orange.connect("toggled", self.on_color_toggled, "orange")
        toolbar.pack_start(self.btn_orange, False, False, 0)

        self.btn_yellow = Gtk.ToggleButton(label="🟡")
        self.btn_yellow.get_style_context().add_class("tag-button2")
        self.btn_yellow.connect("toggled", self.on_color_toggled, "yellow")
        toolbar.pack_start(self.btn_yellow, False, False, 0)

        # 4. Agregar widgets al contenedor principal
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.text_view)

        self.pack_start(toolbar, False, False, 0)
        self.pack_start(scrolled_window, True, True, 0)

    def cargar_resumen(self, archivo_resumen: ArchivoResumen):

        self.text_buffer.set_text("")

        self.archivo_resumen = archivo_resumen

        try:
            html_to_buffer(self.archivo_resumen.cuerpo_texto, self.text_buffer, self.tag_map)
        except Exception as e:
            logger.error(f"Error al cargar el html, cargando en texto plano: {e}")
            self.text_buffer.set_text(self.archivo_resumen.cuerpo_texto)

    def clear_text(self):
        self.text_buffer.set_text("")
        self.archivo_resumen = None

    def guardar_resumen(self):
        texto_fin = self.get_text_html()
        if self.archivo_resumen:
            if self.archivo_resumen.cuerpo_texto == texto_fin:
                return
        else:
            return

        if self.tipo == "nota":
            if self.archivo_resumen.id:
                ServicesArchivoResumen.modificar_archivo_resumen(self.archivo_resumen.id, texto_fin, self.archivo_resumen.titulo)
            else:
                titulo = self.sugerir_titulo()
                ServicesArchivoResumen.agregar_archivo_resumen(self.archivo_resumen.parent_id, texto_fin, titulo)
        elif self.tipo == "carta":
            if self.archivo_resumen.id:
                ServicesArchivoResumen.modificar_archivo_resumen_carta(self.archivo_resumen.id, texto_fin, self.archivo_resumen.titulo)
            else:
                titulo = self.sugerir_titulo()
                ServicesArchivoResumen.agregar_archivo_resumen_carta(self.archivo_resumen.parent_id, texto_fin, titulo)


    def toggle_tag(self, tag_name):
        """Aplica o remueve un tag de estilo a la selección actual."""
        buffer = self.text_buffer

        if buffer.get_has_selection():
            start, end = buffer.get_selection_bounds()
            buffer.apply_tag_by_name(tag_name, start, end)
        self.text_view.grab_focus()


    def get_text(self):
        star_iter, end_iter = self.text_buffer.get_bounds()
        text = self.text_buffer.get_text(star_iter, end_iter, True)
        return text

    def get_text_html(self):
        text = buffer_to_html(self.text_buffer, self.tag_map)
        return text

    def apply_color(self, color_name):
        """Aplica un color a la selección actual y remueve los otros colores."""
        buffer = self.text_buffer

        if buffer.get_has_selection():
            start, end = buffer.get_selection_bounds()

            # Remover todos los tags de color existentes
            buffer.remove_tag(self.tag_red, start, end)
            buffer.remove_tag(self.tag_orange, start, end)
            buffer.remove_tag(self.tag_yellow, start, end)

            # Aplicar el nuevo tag de color
            if color_name == "red":
                buffer.apply_tag(self.tag_red, start, end)
            elif color_name == "orange":
                buffer.apply_tag(self.tag_orange, start, end)
            elif color_name == "yellow":
                buffer.apply_tag(self.tag_yellow, start, end)


    def sugerir_titulo(self):
        start, end_iter = self.text_buffer.get_bounds()
        texto_completo = self.text_buffer.get_text(start, end_iter, False)

        if not texto_completo:
            return ""

        titulo = texto_completo.split('\n', 1)[0].strip()

        longitud_maxima = 50

        if len(titulo) > longitud_maxima:
            posicion_corte = titulo.rfind(" ", 0, longitud_maxima)
            if posicion_corte != -1:
                titulo = titulo[:posicion_corte]
            else:
                titulo = titulo[:longitud_maxima]

        return titulo

    # --- Manejadores de eventos ---

    def on_toggled_bold(self, button):
        self.active_tags["bold"] = button.get_active()
        self.toggle_tag("bold")

    def on_toggled_italic(self, button):
        self.active_tags["italic"] = button.get_active()
        self.toggle_tag("italic")

    def on_insert_text(self, buffer, i, text, length):
        start = i.copy()
        end = i.copy()
        end.backward_chars(len(text))

        if self.active_tags["bold"]:
            buffer.apply_tag(self.tag_bold, end, i)
        if self.active_tags["italic"]:
            buffer.apply_tag(self.tag_italic, end, i)
        if self.active_tags["color"] == "red":
            buffer.apply_tag(self.tag_red, end, i)
        elif self.active_tags["color"] == "orange":
            buffer.apply_tag(self.tag_orange, end, i)
        elif self.active_tags["color"] == "yellow":
            buffer.apply_tag(self.tag_yellow, end, i)

    def on_color_toggled(self, button, color_name):
        """Permite activar/desactivar color. Solo uno puede estar activo a la vez."""
        if button.get_active():
            # Desactivar otros colores
            self.btn_red.set_active(color_name == "red")
            self.btn_orange.set_active(color_name == "orange")
            self.btn_yellow.set_active(color_name == "yellow")

            self.active_tags["color"] = color_name
            self.apply_color(color_name)
        else:
            # Si el botón se desactiva manualmente, se vuelve al texto "sin color"
            self.active_tags["color"] = None
        self.text_view.grab_focus()

    def on_key_press_event(self, widget, event):
        key_name = Gdk.keyval_name(event.keyval)
        is_ctrl_pressed = event.state & Gdk.ModifierType.CONTROL_MASK

        if is_ctrl_pressed:
            if key_name == "b" or key_name == "B":
                press_button(self.btn_bold)
                return True
            elif key_name == "i" or key_name == "I":
                press_button(self.btn_italic)
                return True
            elif key_name == "1":
                press_button(self.btn_red)
                return True
            elif key_name == "2":
                press_button(self.btn_orange)
                return True
            elif key_name == "3":
                press_button(self.btn_yellow)
                return True

        return False