
class EstadoDeAplicacion:

    def __init__(self):

        self.revista_seleccionada = None #Revista cargada
        self.carta_seleccionada = None
        self.autor_seleccionado = None #Autor seleccionado
        self.ventana_nota_abierta = False # Si se encuentra o no abierto el formulario notas
        self.revista_edicion_activa = False #Si la edición se encuentra
        self.autores_edicion_activa = False
        self.correo_edicion_activa = False
        self.correo_new = False
        self.revista_datos_originales = {}
        self.nota_a_cargar_en_grupo_analisis = None

        # Permite actualizar el valor del sb_numero_revista sin reiniciar el proceso de actualización de la revista
        self.sb_numero_revista_actualizado_desde_sistema = None
        self.sb_numero_revista_signal_activo = None

        # Borrar ent_busqueda sin activar búsqueda sql
        self.borrar_text_busqueda_temas_sin_actualizar = False