import ui.gi_setup
from gi.repository import Gtk, GLib, Gdk

import sys
import logging

from config import config
from application_state import EstadoDeAplicacion
from database.connection import DataBaseConnection


# Importar ventana principal
from ui.main_window import MainWindow


#Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s",
    handlers=[logging.FileHandler('app.log'),
              logging.StreamHandler(sys.stdout)
              ]
)

logger = logging.getLogger(__name__)

def setup_app():
    logger.info(f"Iniciando configuración de la aplicación {config.APP_NAME}\n"
                f"- Versión: {config.VERSION}")

    #Temas/estilos
    css_provider = Gtk.CssProvider()
    css_file = "style_02.css"
    try:
        css_provider.load_from_path(f"ui/styles/{css_file}")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    except Exception as e:
        logger.warning(f"No se pudo cargar CSS: {e}")

def handle_exception(exc_type, exc_value, exc_traceback): #Manejo de excepciones
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Excepción no manejada:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

def main(): #Función principal
#    try:
        sys.excepthook = handle_exception

        logger.info("=== Iniciando la aplicación ===")

        #Config inicial
        setup_app()
        app_state = EstadoDeAplicacion()
        DataBaseConnection.open_connection()

        # Crea y muestra ventana principal
        logger.info("Creando ventana principal")
        window = MainWindow(app_state)

        #Conectar señal de cierre
        window.connect("destroy", Gtk.main_quit)

        window.show_all()

        logger.info("Ventana principal mostrada - Se inicia Main loop")

        Gtk.main()

        DataBaseConnection.close_connection()
        logger.info("=== Aplicación finalizada correctamente ===")
        return 0

#    except Exception as e:
#       logger.critical(f"Error crítico al iniciar aplicación: {e}")

if __name__ == "__main__":
    sys.exit(main())

