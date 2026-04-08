import inspect
from typing import Optional
from database.querys import QUERY_REGISTRO_MODIFICACIONES


import mysql.connector as con
from config import Config
import logging

logger = logging.getLogger(__name__)


class DataBaseConnection:

    _connection = None

    @classmethod
    def open_connection(cls):
        if cls._connection is None or not cls._connection.is_connected():
            try:
                cls._connection = con.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD, database
                    =Config.DB_NAME)
                logger.info(f"Conexión establecida")
            except Exception as e:
                logger.error(f"Error conectando a MySQL: {e}")
                raise
        return cls._connection

    @classmethod
    def close_connection(cls):
        if cls._connection and cls._connection.is_connected():
            cls._connection.close()
            cls._connection = None
            logger.info(f"Conexión cerrada")

    @classmethod
    def execute_query(cls, query: str, params: Optional[tuple] = None, select_multiple_results: Optional[bool] = False):
        conector = None
        cursor = None
        result = None

        try:
            conector = cls._connection
            if conector is None:
                logging.error("La conexión no está abierta")
                return False, None

            cursor = conector.cursor(dictionary=True)
            cursor.execute(query, params or ())

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall() if select_multiple_results else cursor.fetchone()
            else:
                conector.commit()

                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    result = cursor.rowcount

                    #Registro en la tabla modificaciones
                    stack = inspect.stack()
                    caller_frame = stack[1]
                    instancia = f"{caller_frame.function} ({caller_frame.filename})"
                    cursor.execute(QUERY_REGISTRO_MODIFICACIONES, params=(query, instancia))
                    conector.commit()

            logger.debug(f"Query ejecutada: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error en query: {query} - {e}")
            if conector:
                conector.rollback()
            raise

        finally:
            if cursor:
                cursor.close()