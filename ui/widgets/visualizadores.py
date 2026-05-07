from gi.repository import Gtk, Gdk, GdkPixbuf, GObject # type: ignore
from models import Nota, Carta
from services import NotaServices, ServicesArchivoResumen, CartaServices, AnalisisService
from utils import to_cartas
from ui.widgets import MsgInfo, MsgSiNo



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
            msgbox = MsgInfo("El id provisto no se encuentra en la lista")
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
                pregunta = MsgSiNo("eliminar resumen")
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
            msgbox = MsgInfo("El id provisto no se encuentra en la lista")
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
                pregunta = MsgSiNo("eliminar resumen")
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
        cartas = to_cartas(cartas)
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