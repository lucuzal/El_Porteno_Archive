from gi.repository import Gtk # type: ignore

class EntradaComentarios:

    def __init__(self):

        self.frame = Gtk.Frame()
        self.scroll = Gtk.ScrolledWindow()
        self.tv = Gtk.TextView()

        #Configurar
        self.scroll.add(self.tv)
        self.frame.add(self.scroll)

        #Establecer propiedades
        self._configurar_widget()

    def _configurar_widget(self):
        self.scroll.set_border_width(3)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(False)

        self.tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.tv.set_accepts_tab(False)

        self.tv.set_left_margin(10)
        self.tv.set_right_margin(10)
        self.tv.set_top_margin(10)
        self.tv.set_bottom_margin(10)

        self.frame.set_shadow_type(Gtk.ShadowType.IN)

    def empaquetar(self) -> Gtk.Widget:
        return self.frame

    def borrar_contenido(self):
        text = Gtk.TextBuffer()
        text.set_text(text="", length=0)
        self.tv.set_buffer(text)

    def set_text(self, texto: str):
        text_buffer = Gtk.TextBuffer()
        text_buffer.set_text(text=texto, length=-1)
        self.tv.set_buffer(text_buffer)

    def get_text(self):
        buffer = self.tv.get_buffer()
        star_iter, end_iter = buffer.get_bounds()
        text = buffer.get_text(star_iter, end_iter, True)
        return text
    
    def set_editable(self, editable: bool):
        if editable:
            self.tv.set_editable(True)
        else:
            self.tv.set_editable(False)