from models import Revista, Carta, Nota, Autor


class EstadoDeAplicacion:

    def __init__(self):

        # Relacionado a Revista y formulario main window
        self.revista_seleccionada: Revista = None #Revista cargada
        self.revista_edicion_activa = False #Si la edición se encuentra
        self.revista_datos_originales = {}

        # Relacionado a correo y cartas
        self.carta_seleccionada: Carta = None
        self.correo_edicion_activa = False
        self.correo_new = False

        # Relacionado a Notas y formulario notas_window
        self.nota_seleccionada: Nota = None # Nota seleccionada con la que se inicia el formulario notas
        self.ventana_nota_abierta = False # Si se encuentra o no abierto el formulario notas
        self.nota_edicion_activa = False
        self.nota_new = False
        self.nota_a_cargar_en_grupo_analisis = None

        # Relacionado a la pestaña autores
        self.autor_seleccionado: Autor = None #Autor seleccionado en la pestaña autores
        self.autores_edicion_activa = False #Si se encuentra activa la edición de autores en Pestaña autores.

        # Permite actualizar el valor del sb_numero_revista sin reiniciar el proceso de actualización de la revista
        self.sb_numero_revista_actualizado_desde_sistema = None
        self.sb_numero_revista_signal_activo = None

        # Borrar ent_busqueda en temas sin activar búsqueda sql
        self.borrar_text_busqueda_temas_sin_actualizar = False