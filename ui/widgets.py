import datetime



import config

from gi.repository import Gtk, Gdk, GLib, GObject, Pango, GdkPixbuf
from models import Nota, Tema, Categoria, ArchivoResumen, Carta
from services import NotaServices, ServicesArchivoResumen, CartaServices, AnalisisService
import utils
import logging

logger = logging.getLogger(__name__)



class MsgBoxSiNo(Gtk.MessageDialog):

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

class MsgBoxInfo(Gtk.MessageDialog):

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

class ListaMulti(Gtk.Box):

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self._lista = []

        #widgets
        self.search = Gtk.SearchEntry()
        self.lista_completa = Gtk.TreeView()
        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.add(self.lista_completa)
        scroll_1.set_vexpand(True)

        self.lista_seleccionada = Gtk.TreeView()
        scroll_2 = Gtk.ScrolledWindow()
        scroll_2.add(self.lista_seleccionada)
        scroll_2.set_vexpand(True)

        self.bt_cargar = Gtk.Button(label="-->")

        #cargar

        box_1.pack_start(self.search, True, True, 0)
        box_1.pack_start(scroll_1, True, True, 0)

        self.pack_start(box_1, False, False, 0)
        self.pack_start(self.bt_cargar, False, False, 0)
        self.pack_start(scroll_2, True, True, 0)

    def set_editable(self, editable: bool = True):
        if editable:
            self.search.set_editable(True)
            self.bt_cargar.set_sensitive(True)
        else:
            self.search.set_editable(False)
            self.bt_cargar.set_sensitive(False)



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

    def cargar_texto(self, fecha: datetime):
        texto = utils.formato_fecha(fecha, "entera_visor")
        self._texto = texto
        self.lb_fecha_revista.set_text(self._texto)

    def mostrar_vacio(self,):
        self._texto = ""
        self.lb_fecha_revista.set_text(self._texto)
        self.definir_estado(estado="pendiente") #formato



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
            self.tv.set_editable(False)
        else:
            self.tv.set_editable(True)

class VisualizadorNotas(Gtk.Box):

    __gsignals__ = {
        # nombre_de_la_senal: (flags, return_type, [lista_de_tipos_de_argumentos])
        "new_resumen": (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self, revista: bool = False, autor: bool = False, icon = GdkPixbuf):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.configuracion = {"revista": revista, "autor": autor}
        self.resumen_icon = icon


        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_border_width(3)
        scroll.set_size_request(1200, 500)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.tn = Gtk.TreeView()

        ls_notas = Gtk.TreeStore(int, int, str, str, str, str, str, bool, bool, str, GdkPixbuf.Pixbuf, int)
        cols_title = ["id", "Rev", "Título", "Paginas", "Dossier", "Sección", "Tipo", "Original", "Relacionado",
                      "Autorxs", "Icono", "id_child"]

        self.tn.set_model(ls_notas)

        for i, title in enumerate(cols_title):
            column = Gtk.TreeViewColumn(title)

            if i == 2: # <--- Título
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                self.renderer_text_col_2 = Gtk.CellRendererText()
                self.renderer_text_col_2.set_property("editable", False)
                self.renderer_text_col_2.connect("edited", self.on_col_2_edited)
                column.pack_start(renderer_pixbuf, False)
                column.pack_start(self.renderer_text_col_2, True)
                column.add_attribute(renderer_pixbuf, "pixbuf", 10)
                column.add_attribute(self.renderer_text_col_2, "text", 2)
                column.set_fixed_width(300)

            elif i == 7 or i == 8: # <---- Original / relacionado {casilla de verificiación}
                renderer_toggle = Gtk.CellRendererToggle()
                column.pack_start(renderer_toggle, True)
                column.add_attribute(renderer_toggle, "active", i)
            elif i == 10:
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                column.pack_start(renderer_pixbuf, False)
                column.add_attribute(renderer_pixbuf, "pixbuf", 10)
                column.set_visible(False)
            elif i == 11:
                column.set_visible(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column.pack_start(renderer_text, True)
                column.add_attribute(renderer_text, "text", i)

                if i == 1 and not revista:
                    column.set_visible(False)
                elif i == 5:
                    column.set_fixed_width(100)
                elif i == 9 and not autor:
                    column.set_visible(False)

            column.set_sort_column_id(i)
            column.set_resizable(True)
            self.tn.append_column(column)


        self.tn.set_activate_on_single_click(False)
        self.tn.set_enable_search(False)

        scroll.add(self.tn)
        self.add(scroll)

        # Conexiones
        self.tn.connect("key-press-event", self.on_key_press_event)
        self.tn.connect("button-press-event", self.on_tn_button_press)

    def borrar_contenido(self):
        ls_notas = self.tn.get_model()
        ls_notas.clear()

    def cargar_notas(self, notas: list[Nota]):

        model = self.tn.get_model()
        model.clear()

        for nota in notas:
            tupla = (nota.id, nota.revista, nota.titulo, nota.paginas, nota.dossier, nota.seccion,
                     nota.tipo, nota.original, nota.relacionado, NotaServices.get_autores_en_una_linea(nota), None, None)
            nota_parent_iter = model.append(None, tupla)

            if len(nota.analisis):
                for archivo in nota.analisis:
                    model.append(nota_parent_iter, [None, None, archivo.titulo, None, None, None, None, False, False, None, self.resumen_icon, archivo.id])


    def seleccionar_nota_segun_id(self, id_nota: int):
        model = self.tn.get_model()
        encontrado = False
        for i, row in enumerate(model):
            if int(id_nota) == row[0]:
                self.tn.set_cursor(Gtk.TreePath(i))
                encontrado = True
        if not encontrado:
            msgbox = MsgBoxInfo("El id provisto no se encuentra en la lista")
            msgbox.show()

    def on_key_press_event(self, widget, event):
        key_name = Gdk.keyval_name(event.keyval)

        if key_name == "Delete":
            self.borrar_fila()

    def borrar_fila(self, widget = None):
        selection = self.tn.get_selection()
        model, i = selection.get_selected()

        if i is not None:
            if model.iter_parent(i):
                pregunta = MsgBoxSiNo("eliminar resumen")
                if pregunta.show() == Gtk.ResponseType.NO:
                    return

                analisis_id = model.get_value(i, 11)
                ServicesArchivoResumen.delete_archivo_resumen_por_id(analisis_id)
                model.remove(i)

    def on_tn_button_press(self, widget, event):
        if event.button == 3:
            path = widget.get_path_at_pos(int(event.x), int(event.y))
            if path is not None:
                path, col, cellx, celly = path
                widget.grab_focus()
                widget.set_cursor(path, col, 0)

            model = widget.get_model()
            i = model.get_iter(path)
            if model.iter_parent(i):
                self.show_context_menu(event, True)
            else:
                self.show_context_menu(event, False)
            return True
        return False

    def show_context_menu(self, event, is_child : bool = False):

        menu = Gtk.Menu()
        menu.attach_to_widget(self.tn, None)

        if not is_child:
            item_edit = Gtk.MenuItem(label="Agregar resumen")
            item_edit.connect("activate", self.on_click_menu_agregar_nota)
            menu.append(item_edit)

        else:
            item_edit = Gtk.MenuItem(label="Eliminar archivo de resumen")
            item_edit.connect("activate", self.borrar_fila)
            menu.append(item_edit)

            item_edit = Gtk.MenuItem(label="Cambiar título")
            item_edit.connect("activate", self.editar_titulo_col_2)
            menu.append(item_edit)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def editar_titulo_col_2(self, widget):
        selection = self.tn.get_selection()
        model, tree_i = selection.get_selected()
        path = model.get_path(tree_i)
        column = self.tn.get_column(2)


        self.renderer_text_col_2.set_property("editable", True)

        self.tn.set_cursor_on_cell(
            path,
            column,
            self.renderer_text_col_2,
            start_editing = True
        )

    def on_col_2_edited(self, widget, path, new_text):
        self.renderer_text_col_2.set_property("editable", False)
        analisis_id = self.tn.get_model()[path][11]
        self.tn.get_model()[path][2] = new_text
        ServicesArchivoResumen.actualizar_titulo(analisis_id, new_text)

    def on_click_menu_agregar_nota(self, widget):
        nota_id = self.obtener_seleccion_por_columna(0)
        self.emit("new_resumen", nota_id)

    def obtener_seleccion_por_columna(self, indice_columna: int):
        selection = self.tn.get_selection()
        model, tree_i = selection.get_selected()
        path = model.get_path(tree_i)
        valor = model[path][indice_columna]
        return valor


class VisualizadorCartas(Gtk.Box):

    __gsignals__ = {
        # nombre_de_la_senal: (flags, return_type, [lista_de_tipos_de_argumentos])
        "new_resumen": (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self, icon = GdkPixbuf):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.resumen_icon = icon

        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.set_border_width(3)
        scroll.set_size_request(1200, 100)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.tc = Gtk.TreeView()

        ls_notas = Gtk.TreeStore(int, int, str, str, bool, GdkPixbuf.Pixbuf, int)
        cols_title = ["id", "Rev", "Remitentes", "Tema", "Relevante", "Icono", "id_child"]

        self.tc.set_model(ls_notas)
        self.grupo_activo = None

        for i, title in enumerate(cols_title):
            column = Gtk.TreeViewColumn(title)

            if i == 2: # <--- Título
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                self.renderer_text_col_2 = Gtk.CellRendererText()
                self.renderer_text_col_2.set_property("editable", False)
                self.renderer_text_col_2.connect("edited", self.on_col_2_edited)
                column.pack_start(renderer_pixbuf, False)
                column.pack_start(self.renderer_text_col_2, True)
                column.add_attribute(renderer_pixbuf, "pixbuf", 5)
                column.add_attribute(self.renderer_text_col_2, "text", 2)
                column.set_fixed_width(300)
            elif i == 3: # <---- Columna tema
                renderer_text = Gtk.CellRendererText()
                column.pack_start(renderer_text, True)
                column.add_attribute(renderer_text, "text", i)
                column.set_fixed_width(710)
            elif i == 4: # <---- Original / relacionado {casilla de verificiación}
                renderer_toggle = Gtk.CellRendererToggle()
                column.pack_start(renderer_toggle, True)
                column.add_attribute(renderer_toggle, "active", i)
            elif i == 5:
                renderer_pixbuf = Gtk.CellRendererPixbuf()
                column.pack_start(renderer_pixbuf, False)
                column.add_attribute(renderer_pixbuf, "pixbuf", 5)
                column.set_visible(False)
            elif i == 6:
                    column.set_visible(False)
            else:
                renderer_text = Gtk.CellRendererText()
                column.pack_start(renderer_text, True)
                column.add_attribute(renderer_text, "text", i)

            column.set_sort_column_id(i)
            column.set_resizable(True)
            self.tc.append_column(column)


        self.tc.set_activate_on_single_click(False)
        self.tc.set_enable_search(False)

        scroll.add(self.tc)
        self.add(scroll)

        # Conexiones
        self.tc.connect("key-press-event", self.on_key_press_event)
        self.tc.connect("button-press-event", self.on_tn_button_press)

    def borrar_contenido(self):
        ls_notas = self.tc.get_model()
        ls_notas.clear()

    def cargar_cartas(self, cartas: list[Carta], tag_activo):

        model = self.tc.get_model()
        model.clear()

        for carta in cartas:
            tupla = (carta.id, carta.revista, carta.remitente, carta.tema, carta.relevante, None, None)
            carta_parent_iter = model.append(None, tupla)

            if carta.archivo_resumen:
                for archivo in carta.archivo_resumen:
                    model.append(carta_parent_iter, [None, None, archivo.titulo, None, False, self.resumen_icon, archivo.id])

        self.grupo_activo = tag_activo

    def seleccionar_nota_segun_id(self, id_carta: int):
        model = self.tc.get_model()
        encontrado = False
        for i, row in enumerate(model):
            if int(id_carta) == row[0]:
                self.tc.set_cursor(Gtk.TreePath(i))
                encontrado = True
        if not encontrado:
            msgbox = MsgBoxInfo("El id provisto no se encuentra en la lista")
            msgbox.show()

    def on_key_press_event(self, widget, event):
        key_name = Gdk.keyval_name(event.keyval)

        if key_name == "Delete":
            self.borrar_fila()

    def borrar_fila(self, widget = None):
        selection = self.tc.get_selection()
        model, i = selection.get_selected()

        if i is not None:
            if model.iter_parent(i):
                pregunta = MsgBoxSiNo("eliminar resumen")
                if pregunta.show() == Gtk.ResponseType.NO:
                    return

                analisis_id = model.get_value(i, 6)
                CartaServices.borrar_archivo_resumen_en_carta(analisis_id)
                model.remove(i)

    def on_tn_button_press(self, widget, event):
        if event.button == 3:
            path = widget.get_path_at_pos(int(event.x), int(event.y))
            if path is not None:
                path, col, cellx, celly = path
                widget.grab_focus()
                widget.set_cursor(path, col, 0)

            model = widget.get_model()
            i = model.get_iter(path)
            if model.iter_parent(i):
                self.show_context_menu(event, True)
            else:
                self.show_context_menu(event, False)
            return True
        return False

    def show_context_menu(self, event, is_child : bool = False):

        menu = Gtk.Menu()
        menu.attach_to_widget(self.tc, None)

        if not is_child:
            item_edit = Gtk.MenuItem(label="Eliminar carta de categoría")
            item_edit.connect("activate", self.on_eliminar_carta_de_categoria)
            menu.append(item_edit)

            item_edit = Gtk.MenuItem(label="Agregar resumen")
            item_edit.connect("activate", self.on_click_menu_agregar_resumen)
            menu.append(item_edit)

        else:
            item_edit = Gtk.MenuItem(label="Eliminar archivo de resumen")
            item_edit.connect("activate", self.borrar_fila)
            menu.append(item_edit)

            item_edit = Gtk.MenuItem(label="Cambiar título")
            item_edit.connect("activate", self.editar_titulo_col_2)
            menu.append(item_edit)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def on_eliminar_carta_de_categoria(self, widget):
        seleccion = self.tc.get_selection()
        model, i = seleccion.get_selected()
        carta_id = model.get_value(i,0)

        CartaServices.quitar_carta_del_grupo_de_analisis(carta_id, self.grupo_activo)

        self.actualizar(self.grupo_activo)

    def actualizar(self, tag_id):
        cartas = AnalisisService.get_cartas_por_grupo_analisis(tag_id)
        cartas = utils.to_cartas(cartas)
        self.cargar_cartas(cartas, tag_id)



    def editar_titulo_col_2(self, widget):
        selection = self.tc.get_selection()
        model, tree_i = selection.get_selected()
        path = model.get_path(tree_i)
        column = self.tc.get_column(2)


        self.renderer_text_col_2.set_property("editable", True)

        self.tc.set_cursor_on_cell(
            path,
            column,
            self.renderer_text_col_2,
            start_editing = True
        )

    def on_col_2_edited(self, widget, path, new_text):
        self.renderer_text_col_2.set_property("editable", False)
        analisis_id = self.tc.get_model()[path][6]
        self.tc.get_model()[path][2] = new_text
        CartaServices.actualizar_titulo_de_archivo_resumen(analisis_id, new_text)

    def on_click_menu_agregar_resumen(self, widget):
        carta_id = self.obtener_seleccion_por_columna(0)
        self.emit("new_resumen", carta_id)

    def obtener_seleccion_por_columna(self, indice_columna: int):
        selection = self.tc.get_selection()
        model, tree_i = selection.get_selected()
        path = model.get_path(tree_i)
        valor = model[path][indice_columna]
        return valor


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
            utils.html_to_buffer(self.archivo_resumen.cuerpo_texto, self.text_buffer, self.tag_map)
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
        text = utils.buffer_to_html(self.text_buffer, self.tag_map)
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
                utils.press_button(self.btn_bold)
                return True
            elif key_name == "i" or key_name == "I":
                utils.press_button(self.btn_italic)
                return True
            elif key_name == "1":
                utils.press_button(self.btn_red)
                return True
            elif key_name == "2":
                utils.press_button(self.btn_orange)
                return True
            elif key_name == "3":
                utils.press_button(self.btn_yellow)
                return True

        return False


class TextEditor_Back_up(Gtk.Box):
    def __init__(self, archivo_resumen: ArchivoResumen):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_border_width(10)

        # Estado del formato =
        self.active_tags = {
            "bold": False,
            "italic": False,
            "color": None
        }

        self.archivo_resumen = archivo_resumen

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
            "red": self.tag_red,
            "orange": self.tag_orange,
            "yellow": self.tag_yellow
        }

        try:
            utils.html_to_buffer(self.archivo_resumen.cuerpo_texto, self.text_buffer, self.tag_map)
        except Exception as e:
            logger.error(f"Error al cargar el html, cargando en texto plano: {e}")
            self.text_buffer.set_text(self.archivo_resumen.cuerpo_texto)

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

    def cargar_resumen(self):
        pass

    def guardar_resumen(self):
        texto_fin = self.get_text_html()
        if self.archivo_resumen.cuerpo_texto == texto_fin:
            return

        if self.archivo_resumen.id:
            ServicesArchivoResumen.modificar_archivo_resumen(self.archivo_resumen.id, texto_fin,
                                                             self.archivo_resumen.titulo)
        else:
            titulo = self.sugerir_titulo()
            ServicesArchivoResumen.agregar_archivo_resumen(self.archivo_resumen.parent_id, texto_fin, titulo)

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
        text = utils.buffer_to_html(self.text_buffer, self.tag_map)
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
                utils.press_button(self.btn_bold)
                return True
            elif key_name == "i" or key_name == "I":
                utils.press_button(self.btn_italic)
                return True
            elif key_name == "1":
                utils.press_button(self.btn_red)
                return True
            elif key_name == "2":
                utils.press_button(self.btn_orange)
                return True
            elif key_name == "3":
                utils.press_button(self.btn_yellow)
                return True

        return False
