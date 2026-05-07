
from gi.repository import Gtk # type: ignore

class MsgSiNo(Gtk.MessageDialog):

    def __init__(self,  tipo: str = "Descartar"):
        super().__init__(parent=None,
        flags=Gtk.DialogFlags.MODAL,
        type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO)

        if tipo == "Descartar":
            self.set_property("text", "Ha realizado cambios. ¿Está seguro que desea descartarlos?")
            self.set_title("Descartar cambios")
        elif tipo == "Agregar_grupo":
            self.set_property("text", "¿Está seguro que desea agregar un grupo de análisis?")
            self.set_property("secondary-text", "El mismo solo puede borrarse directamente desde la base de datos")
            self.set_title("Agregar grupo de análisis")
        elif tipo == "eliminar resumen":
            self.set_property("text", "¿Está seguro que desea eliminar el archivo resumen?")
            self.set_title("Eliminar Archivo Resumen")

    def show(self):
        response = self.run()
        self.destroy()
        return response
    
class MsgInfo(Gtk.MessageDialog):

    def __init__(self, text):
        super().__init__(parent=None,
        flags=Gtk.DialogFlags.MODAL,
        type=Gtk.MessageType.INFO,
        buttons=Gtk.ButtonsType.OK,
        message_format=text)

        # Establecer el título del diálogo
        self.set_title("Atención")

    def show(self):
        self.run()
        self.destroy()