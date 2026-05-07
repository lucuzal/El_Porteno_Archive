from gi.repository import Gtk #type: ignore
from ui.widgets import EntradaComentarios, MsgInfo
from models import Autor, Tema
from utils import buscar_similares

class DialogAddAutor(Gtk.Window):
    
    def __init__(self, cadena: str, listado_a_comprobar: list[Autor], on_confirm):
        Gtk.Window.__init__(self, title=f"Agregar autor en base a {cadena}")
        self.set_border_width(10)
        self.set_default_size(600, 200)

        self._on_confirm = on_confirm
        self._cadena: str = cadena
        self._listado_a_comprobar: list[Autor] = listado_a_comprobar
        self._comprobacion_pendiente: bool = True
        self._autor_a_cargar: Autor = None
        self._setup_ui()
        self._connect_signals()
        self._iniciar()

    def _setup_ui(self):
        
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.add(grid)

        #Crear widgets:
        lb_nombre = Gtk.Label(label="Nombre: ")
        lb_apellido = Gtk.Label(label="Apellido ")
        lb_genero = Gtk.Label(label="Genero: ")
        lb_comentarios = Gtk.Label("Comentarios: ")
        self.lb_duplicados = Gtk.Label()
        self.lb_duplicados.set_markup('<span size="120%">Usted está por ingresar un nuevo autor</span>')

        self.ent_nombre = Gtk.Entry()
        self.ent_apellido = Gtk.Entry()
        self.txt_comentarios = EntradaComentarios()

        ls_items = Gtk.ListStore(str, str)
        items = (["Fem", "Femenino"], ["Masc", "Masculino"], ["NoA","No aplica"], ["Otrx","Otrx"])
        for i in items: ls_items.append(i)
        self.cb_genero = Gtk.ComboBox.new_with_model(ls_items)
        rendered_text = Gtk.CellRendererText()
        self.cb_genero.pack_start(rendered_text, True)
        self.cb_genero.add_attribute(rendered_text, "text", 1)
        self.cb_genero.set_active(-1)

        self.bt_ingresar = Gtk.Button(label="Ingresar")
        self.bt_cancelar = Gtk.Button(label="cancelar")

        grid.attach(lb_nombre,0,0,1,1) #fila 0
        grid.attach(self.ent_nombre, 1,0,1,1) #fila 0
        grid.attach(self.bt_ingresar, 2,0,1,1) # fila 0
        grid.attach(lb_apellido, 0, 1, 1, 1) # fila 1
        grid.attach(self.ent_apellido, 1, 1, 1, 1) # fila 1
        grid.attach(self.bt_cancelar, 2, 1, 1, 1) #  fila 1
        grid.attach(lb_genero, 0, 2, 1, 1) # fila 2
        grid.attach(self.cb_genero, 1, 2, 1, 1) # fila 2D
        grid.attach(lb_comentarios, 0, 3, 1, 1) # fila 3
        grid.attach(self.txt_comentarios.empaquetar(), 1, 3, 1, 1) #fila 3
        grid.attach(self.lb_duplicados, 1, 4, 1, 1) # fila 4

    def _connect_signals(self):
        self.bt_cancelar.connect("clicked", self._bt_cancelar_clicked)
        self.bt_ingresar.connect("clicked", self._bt_ingresar_clicked)

    def _iniciar(self):
        self.ent_apellido.set_text(self._cadena)
        self._habilitar_edicion()
    
    def _habilitar_edicion(self, editable: bool =True):
        if editable:
            self.ent_nombre.set_editable(True)
            self.ent_apellido.set_editable(True)
            self.cb_genero.set_sensitive(True)
            self.txt_comentarios.set_editable(True)
        else:
            self.ent_nombre.set_editable(False)
            self.ent_apellido.set_editable(False)
            self.cb_genero.set_sensitive(False)
            self.txt_comentarios.set_editable(False)

    def _get_values_from_widgets(self) -> dict:
        
        nombre = self.ent_nombre.get_text()
        apellido = self.ent_apellido.get_text()
        row = self.cb_genero.get_active()
        genero = self.cb_genero.get_model()[row][0] if not row == -1 else None 
        comentarios = self.txt_comentarios.get_text()

        data = {
            'nombre': nombre,
            'apellido': apellido,
            'genero': genero,
            'comentarios': comentarios
        }

        return data
    
    def _data_to_autor(self, data: dict) -> Autor:
        return Autor(data["nombre"], data["apellido"], data["genero"], data["comentarios"])
    
    def _check_apellido(self) -> bool:
        return False if self.ent_apellido.get_text() == "" else True 
    
    # FUNCIONES DERIVADAS DEL SIGNALS DE WIDGETS

    def _bt_cancelar_clicked(self, widget: Gtk.Button):
        if self._comprobacion_pendiente:
            self.close()
        else:
            self._habilitar_edicion()
            widget.set_label("Cancelar")
            self._comprobacion_pendiente = True
            self.lb_duplicados.set_label("")

    def _bt_ingresar_clicked(self, widget):
        
        if self._comprobacion_pendiente:
            data = self._get_values_from_widgets()
            if data["apellido"] == "" or data["genero"] is None:
                mensaje = MsgInfo("Apellido y género son campos obligatorios")
                mensaje.show()
                return
            self._habilitar_edicion(False)
            self._autor_a_cargar = self._data_to_autor(data)
            similares = buscar_similares(self._autor_a_cargar.nombre_completo(), self._listado_a_comprobar, es_autor=True)

            if len(similares) > 0:
                self._comprobacion_pendiente = False
                self.bt_ingresar.set_label("Confirmar")
                self.bt_cancelar.set_label("Volver a edición")
                text_markup = '<span size="120%">Compruebe no duplicar autores: \n'
                for i, e in enumerate(similares):
                    if i == len(similares) -1:
                        text_markup += f"{e}.</span>"
                    else:
                        text_markup += f"{e},\n"
                self.lb_duplicados.set_markup(text_markup)
            else:
                self._on_confirm(self._autor_a_cargar)
                self.close()
        else:
            self._on_confirm(self._autor_a_cargar)
            self.close()
                
    def on_destroy(self):
        pass
        
class DialogAddTema(Gtk.Window):
    
    def __init__(self, cadena: str, listado_a_comprobar: list[Autor], on_confirm):
        Gtk.Window.__init__(self, title=f"Agregar tema en base a {cadena}")
        self.set_border_width(10)
        self.set_default_size(400, 200)

        self._on_confirm = on_confirm
        self._cadena: str = cadena
        self._listado_a_comprobar = listado_a_comprobar
        self._comprobacion_pendiente: bool = True
        self._tema_a_cargar: Tema = None
        self._setup_ui()
        self._connect_signals()
        self._iniciar()

    def _setup_ui(self):

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.add(grid)

        #Crear widgets:
        lb_tema = Gtk.Label(label="Tema: ")
        self.lb_duplicados = Gtk.Label()
        self.lb_duplicados.set_markup('<span size="120%">Usted está por ingresar un nuevo tema</span>')

        self.ent_tema = Gtk.Entry()

        self.bt_ingresar = Gtk.Button(label="Ingresar")
        self.bt_cancelar = Gtk.Button(label="cancelar")

        grid.attach(lb_tema,0,0,1,1) #fila 0
        grid.attach(self.ent_tema, 1,0,1,1) #fila 0
        grid.attach(self.bt_ingresar, 2,0,1,1) # fila 0
        grid.attach(self.bt_cancelar, 2, 1, 1, 1) #  fila 1
        grid.attach(self.lb_duplicados, 1, 2, 1, 1) # fila 4

    def _connect_signals(self):
        self.bt_cancelar.connect("clicked", self._bt_cancelar_clicked)
        self.bt_ingresar.connect("clicked", self._bt_ingresar_clicked)

    def _iniciar(self):
        self.ent_tema.set_text(self._cadena)
        self._habilitar_edicion()

    def _habilitar_edicion(self, editable: bool = True):
        if editable:
            self.ent_tema.set_editable(True)
        else:
            self.ent_tema.set_editable(False)

    def _get_values_from_widgets(self) -> dict:
            return self.ent_tema.get_text()

        
    # FUNCIONES DERIVADAS DEL SIGNALS DE WIDGETS

    def _bt_cancelar_clicked(self, widget: Gtk.Button):
        if self._comprobacion_pendiente:
            self.close()
        else:
            self._habilitar_edicion()
            widget.set_label("Cancelar")
            self._comprobacion_pendiente = True
            self.lb_duplicados.set_label("")

    def _bt_ingresar_clicked(self, widget):
            
        if self._comprobacion_pendiente:
            data = self._get_values_from_widgets()
            if data == "":
                mensaje = MsgInfo("El campo tema no puede estar vacío")
                mensaje.show()
                return
            self._habilitar_edicion(False)
            self._tema_a_cargar = Tema(data)
            similares = buscar_similares(self._tema_a_cargar.tema, self._listado_a_comprobar, es_autor=False)

            if len(similares) > 0:
                self._comprobacion_pendiente = False
                self.bt_ingresar.set_label("Confirmar")
                self.bt_cancelar.set_label("Volver a edición")
                text_markup = '<span size="120%">Compruebe no duplicar temas: \n'
                for i, e in enumerate(similares):
                    if i == len(similares) -1:
                        text_markup += f"{e}.</span>"
                    else:
                        text_markup += f"{e},\n"
                self.lb_duplicados.set_markup(text_markup)
            else:
                self._on_confirm(self._tema_a_cargar)
                self.close()
        else:
            self._on_confirm(self._tema_a_cargar)
            self.close()
                    
    def on_destroy(self):
            pass