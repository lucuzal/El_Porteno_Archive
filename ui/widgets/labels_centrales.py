from gi.repository import Gtk, Gdk #type: ignore
from datetime import date
from utils import formato_fecha

class FechaRevista(Gtk.Box):

    def __init__(self):
        super().__init__()
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.98, .29, .37, 1))
        self.lb_fecha_revista = Gtk.Label()
        self._texto = ""
        self.lb_fecha_revista.set_text(self._texto)
        self.lb_fecha_revista.set_justify(Gtk.Justification.CENTER)
        self.pack_start(self.lb_fecha_revista, True, True, 0)

    def definir_estado(self, estado: str = "pendiente",edicion_activa: bool = False):
        if not edicion_activa:
            if estado == "pendiente":
                self.lb_fecha_revista.set_markup(f"<span foreground=\"#292929\" size=\"large\">"
                                            f"<b>{self._texto}</b></span>")
                self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.5, .5, .5, .5))
            elif estado == "missing":
                self.lb_fecha_revista.set_markup(f"<span foreground=\"#7A000E\" size=\"large\">"
                                                 f"<b>{self._texto}</b></span>")
                self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.98, .29, .37, 1))
            elif estado == "cargado":
                self.lb_fecha_revista.set_markup(f"<span foreground=\"#2F4701\" size=\"large\">"
                                         f"<b>{self._texto}</b></span>")
                self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.74, .87, .49, 1))
        else:
            self.lb_fecha_revista.set_markup(f"<span foreground=\"#002454\" size=\"large\">"
                                         f"<b>{self._texto} - EDICIÓN ACTIVA</b></span>")
            self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.58, .79, 1, 1))

    def cargar_texto(self, fecha: date):
        texto = formato_fecha(fecha, "entera_visor")
        self._texto = texto
        self.lb_fecha_revista.set_text(self._texto)

    def mostrar_vacio(self,):
        self._texto = ""
        self.lb_fecha_revista.set_text(self._texto)
        self.definir_estado(estado="pendiente") #formato



class LabelNota(Gtk.Box):

    def __init__(self):
        super().__init__()
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.98, .29, .37, 1))
        self.lb_nota_id = Gtk.Label()
        self._texto = "Nota ID° XXXX"
        self._estado = "visualizacion"
        self.lb_nota_id.set_text(self._texto)
        self.pack_start(self.lb_nota_id, True, True, 0)

    def formato_en_edicion(self):
        self.lb_nota_id.set_markup(f"<span foreground=\"#002454\">"
                                         f"<big><b>{self._texto} - EDICIÓN ACTIVA</b></big></span>")
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.58, .79, 1, 1))
        self._estado = "edicion_activa"


    def formato_nota_nueva(self):
        self.lb_nota_id.set_markup(f"<span foreground=\"#B36E44\">"
                                   f"<big><b>Nota ID° XXXX </b></big></span>")
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.224, .162, .85, 1))
        self._estado = "nueva"

    def formato_visualizacion(self):
        self.lb_nota_id.set_markup(f"<span foreground=\"#2F4701\">"
                                   f"<big><b>{self._texto}</b></big></span>")
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(.74, .87, .49, 1))
        self._estado = "visualizacion"

    def actualizar_nota(self, nota_id = 0):
        if not nota_id:
            self.formato_nota_nueva()
        else:
            self._texto = f"Nota ID° {nota_id}"
            if self._estado == "visualizacion":
                self.formato_visualizacion()
            else:
                self.formato_en_edicion()