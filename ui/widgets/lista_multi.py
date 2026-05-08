from gi.repository import Gtk #type: ignore
from models import Tema, Autor
from ui.dialogs import DialogAddAutor, DialogAddTema

class ListaMulti(Gtk.Box):

    def __init__(self, es_autor: bool):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self._lista: set[Autor | Tema] = set()
        self._full_elementos: list[Autor | Tema] = []
        self._filtrado_elementos: list[Autor | Tema] = []
        self._elementos_creados: set[Autor | Tema] = set()
        self._es_autor: bool = es_autor


        #widgets
        self._ent_search = Gtk.SearchEntry()
        self._tv_lista_completa = Gtk.TreeView()
        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.add(self._tv_lista_completa)
        scroll_1.set_vexpand(True)
        scroll_1.set_min_content_height(200)
        ls_f = Gtk.ListStore(int, str)
        ls_f.append([0,""])
        self._tv_lista_completa.set_model(ls_f)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("id", renderer, text=0)
        column.set_resizable(False)
        column.set_visible(False)
        self._tv_lista_completa.append_column(column)
        column = Gtk.TreeViewColumn("Nombre", renderer, text=1)
        column.set_resizable(False)
        column.set_visible(True)
        self._tv_lista_completa.append_column(column)
        self._tv_lista_completa.set_headers_visible(False)
        self._tv_lista_completa.set_enable_search(False)


        self._tv_lista_seleccionada = Gtk.TreeView()
        scroll_2 = Gtk.ScrolledWindow()
        scroll_2.add(self._tv_lista_seleccionada)
        scroll_2.set_vexpand(True)
        ls_s = Gtk.ListStore(int, str)
        ls_s.append([0,""])
        self._tv_lista_seleccionada.set_model(ls_s)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("id", renderer, text=0)
        column.set_resizable(False)
        column.set_visible(False)
        self._tv_lista_seleccionada.append_column(column)
        column = Gtk.TreeViewColumn("Nombre", renderer, text=1)
        column.set_resizable(False)
        column.set_visible(True)
        self._tv_lista_seleccionada.append_column(column)
        self._tv_lista_seleccionada.set_headers_visible(False)
        self._tv_lista_seleccionada.set_enable_search(False)
        

        self._bt_cargar = Gtk.Button(label="-->")

        self._connect_signals()

        #cargar

        box_1.pack_start(self._ent_search, True, True, 0)
        box_1.pack_start(scroll_1, True, True, 0)

        self.pack_start(box_1, False, False, 0)
        self.pack_start(self._bt_cargar, False, False, 0)
        self.pack_start(scroll_2, True, True, 0)

    def _connect_signals(self):
        self._ent_search.connect("changed", self._search_changed)
        self._tv_lista_completa.connect("row_activated", self._lista_completa_row_activated)
        self._bt_cargar.connect("clicked", self._bt_cargar_clicked)
        self._tv_lista_seleccionada.connect("row_activated", self._lista_seleccionada_row_activated)
        self._ent_search.connect("activate", self._search_activated)

    def _seleccionar_elemento(self, elemento: Autor | Tema): #Selecciona del listado largo
        self._lista.add(elemento)
        self._cargar_lista_en_treeview()

    def _get_id_from_tree_view_selection(self, widget: Gtk.TreeView, path: Gtk.TreePath) -> int:
        model = widget.get_model()
        i = model.get_iter(path)
        return model.get_value(i,0)
    
    def _get_name_from_tree_view_selection(self, widget: Gtk.TreeView, path: Gtk.TreePath) -> str:
        model = widget.get_model()
        i = model.get_iter(path)
        return model.get_value(i,1)
    
    def _get_id_and_name_from_tree_view_selection(self, widget: Gtk.TreeView, path: Gtk.TreePath) -> tuple[int,str]:
        id = self._get_id_from_tree_view_selection(widget, path)
        name = self._get_name_from_tree_view_selection(widget, path)
        return id, name 
    
    def _cargar_lista_en_treeview(self): #Carga los elementos seleccionados (_lista) en el treeview
        ls = self._tv_lista_seleccionada.get_model()
        ls.clear()
        
        if self._lista:
            if self._es_autor:
                for e in self._lista:
                        ls.append([e.id, e.nombre_completo()]) if e.id else ls.append([0, e.nombre_completo()])
            else:
                for e in self._lista:
                    ls.append([e.id, e.tema]) if e.id else ls.append([0, e.tema])

    def get_selection(self) -> set[Autor | Tema]:
        return self._lista
 
    def set_editable(self, editable: bool = True): #Configura el widget si es editable o no
        if editable:
            self._ent_search.set_editable(True)
            self._bt_cargar.set_sensitive(True)
        else:
            self._ent_search.set_editable(False)
            self._bt_cargar.set_sensitive(False)
            self._full_elementos = []

    def set_elementos_seleccionados_full(self, ingresado: set[Autor | Tema]): #Carga los elementos seleccionados para esa nota
        self._lista = ingresado.copy()
        self._cargar_lista_en_treeview()

    def cargar_todos_los_elementos(self, elementos: tuple[Autor | Tema]): #Carga todos los elementos para buscar entre ellos
        self._full_elementos = elementos
        ls = self._tv_lista_completa.get_model()
        ls.clear()

        if self._full_elementos:
            if self._es_autor:
                for e in self._full_elementos:
                    ls.append([e.id, e.nombre_completo(True)])
            else:
                for e in self._full_elementos:
                    ls.append([e.id, e.tema])


    def cargar_elementos_filtrados(self, elementos: list[Autor | Tema]): #Filtra el treeview según se escribe en self.search (Entry)
        self._filtrado_elementos = elementos
        ls = self._tv_lista_completa.get_model()
        ls.clear()

        if self._filtrado_elementos:
            if self._es_autor:
                for e in self._filtrado_elementos:
                    ls.append([e.id, e.nombre_completo(True)])
            else:
                for e in self._filtrado_elementos:
                    ls.append([e.id, e.tema])

    def clear(self): #Borra todo lo cargado
        ls: Gtk.ListStore = self._tv_lista_seleccionada.get_model()
        ls.clear()
        self._lista.clear()


    # SEÑALES ACTIVADAS POR WIDGETS

    def _search_changed(self, widget: Gtk.Entry):
        cadena:str = widget.get_text().lower()

        def coincide_autor(e: Autor) -> bool:
            return (cadena in e.nombre.lower() 
                    or cadena in e.apellido.lower() 
                    or cadena in e.nombre_completo().lower()
                    or cadena in e.nombre_completo(True).lower())
        
        def coincide_tema(e: Tema) -> bool:
            return cadena in e.tema.lower() 

        resultado = []
        if self._es_autor:
            resultado = list(filter(coincide_autor, self._full_elementos)) 
        else:
            resultado = list(filter(coincide_tema, self._full_elementos)) 
        
        self.cargar_elementos_filtrados(resultado)
    
    def _lista_completa_row_activated(self, widget: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn):
        id_from_widget: int = self._get_id_from_tree_view_selection(widget, path)
        elemento: Autor | Tema = None
        if not id_from_widget == 0:
            if self._filtrado_elementos:
                elemento = next((e for e in self._filtrado_elementos if (e.id == id_from_widget)),None)
            else:
                elemento = next((e for e in self._full_elementos if (e.id == id_from_widget)),None)

        if elemento:
            self._seleccionar_elemento(elemento)

    def _bt_cargar_clicked(self, widget: Gtk.Button):
        selection = self._tv_lista_completa.get_selection()
        model, tree_iter = selection.get_selected()
        if tree_iter is None:
            return
        path = model.get_path(tree_iter)
        self._tv_lista_completa.emit("row_activated", path, None) #None en Column

    def _lista_seleccionada_row_activated(self, widget: Gtk.TreeView, path:Gtk.TreePath, column:Gtk.TreeViewColumn):
        id_from_widget, name_from_widget = self._get_id_and_name_from_tree_view_selection(widget, path)
        elemento: Autor | Tema = None
        n_elementos_cargados = len(self._lista)
        
        if n_elementos_cargados == 1:
            self._lista.clear()
        elif n_elementos_cargados > 1:
            if id_from_widget == 0:
                if self._es_autor:
                    elemento = next((e for e in self._lista if (e.nombre_completo() == name_from_widget)), None)
                else:
                    elemento = next((e for e in self._lista if (e.tema() == name_from_widget)), None)
            else:
                elemento = next((e for e in self._lista if (e.id == id_from_widget)), None)
                self._lista.remove(elemento)

        self._cargar_lista_en_treeview()

    def _search_activated(self, widget: Gtk.Entry):
        
        def on_elemento_confirmado(elemento: Autor | Tema):
            self._seleccionar_elemento(elemento)
            self._elementos_creados.add(elemento)
        
        cadena = widget.get_text()

        if not cadena or cadena == "": return #Si se da enter con la cadena vacía, no pasa nada

        n_elementos = len(self._filtrado_elementos)

        if n_elementos == 1: #Si da enter con un solo elemento en la lista, (o se crea elemento nuevo o se ingresa)
            self._seleccionar_elemento(self._filtrado_elementos[0])
        elif n_elementos == 0:
            if self._es_autor:
                dialog = DialogAddAutor(cadena, self._full_elementos, on_elemento_confirmado)
                ventana_padre = self.get_toplevel()
                dialog.set_transient_for(ventana_padre)
                dialog.set_modal(True)
                #Señal de cierre
                dialog.connect("destroy", self._on_dialog_close)
                dialog.show_all()
            else:
                dialog = DialogAddTema(cadena, self._full_elementos, on_elemento_confirmado)
                ventana_padre = self.get_toplevel()
                dialog.set_transient_for(ventana_padre)
                dialog.set_modal(True)
                #Señal de cierre
                dialog.connect("destroy", self._on_dialog_close)
                dialog.show_all()
        else:
            self._tv_lista_completa.set_cursor(Gtk.TreePath(0))
            self._tv_lista_completa.grab_focus()

    def _on_dialog_close(self, window: Gtk.Window):
        pass

