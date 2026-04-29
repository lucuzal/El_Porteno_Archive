from symtable import Class

from database.connection import DataBaseConnection
from database.querys import (QUERY_CONFIGURACION_INICIAL,
                             QUERY_GET_LAST_ID_OPEN,
                             QUERY_GET_REVISTA_POR_ID,
                             QUERY_GET_STAFF_POR_ID_REVISTA,
                             QUERY_GET_NOTAS_POR_ID_REVISTA,
                             QUERY_GET_AUTOR_DE_NOTA_POR_NOTA_ID,
                             QUERY_GET_TEMAS_DE_NOTA_POR_NOTA_ID,
                             QUERY_GET_CARTAS_POR_REVISTA_ID,
                             QUERY_UPDATE_REVISTA_POR_ID,
                             QUERY_GET_NOTA_POR_ID_NOTA,
                             QUERY_GET_AUTORES_POR_NOMBRE,
                             QUERY_GET_AUTOR_POR_ID_NOMBRE,
                             QUERY_GET_NOTAS_POR_AUTOR,
                             QUERY_UPDATE_AUTOR,
                             QUERY_GET_TEMAS_POR_TEMA,
                             QUERY_BASE_TEMAS_POR_NOTAS,
                             QUERY_BASE_NOTAS_POR_TEMAS,
                             QUERY_GET_CATEGORIAS_POR_NOTA_ID,
                             QUERY_GET_ARCHIVO_RESUMEN_POR_NOTA_ID,
                             QUERY_GET_GRUPOS_ANALISIS,
                             QUERY_AGREGAR_GRUPO_ANALISIS,
                             QUERY_GET_NOTAS_POR_GRUPO_ANALISIS,
                             QUERY_CARGAR_NOTA_AL_GRUPO_ANALISIS,
                             QUERY_DELETE_NOTA_DE_GRUPO_DE_ANALISIS,
                             QUERY_AGREGAR_ARCHIVO_RESUMEN,
                             QUERY_MODIFICAR_ARCHIVO_RESUMEN,
                             QUERY_GET_ARCHIVO_RESUMEN,
                             QUERY_DELETE_ARCHIVO_RESUMEN,
                             QUERY_ACTUALIZAR_TITULO,
                             QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID_CARTA,
                             QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID,
                             QUERY_DELETE_ARCHIVO_RESUMEN_CARTA,
                             QUERY_ACTUALIZAR_TITULO_ARCHIVO_RESUMEN_CARTA,
                             QUERY_GET_CARTAS_POR_GRUPO_ANALISIS,
                             QUERY_GET_GRUPOS_ANALISIS_PARA_CARTA,
                             QUERY_GUARDAR_NUEVA_CARTA,
                             QUERY_UPDATE_CARTA,
                             QUERY_ADD_CARTA_A_GRUPO_ANALISIS,
                             QUERY_AGREGAR_ARCHIVO_RESUMEN_CARTA,
                             QUERY_MODIFICAR_ARCHIVO_RESUMEN_CARTA,
                             QUERY_DELETE_CARTA_DE_GRUPO_ANALISIS,
                             QUERY_GET_AUTORES_POR_REVISTA,
                             QUERY_GET_TEMAS_POR_REVISTA,
                             QUERY_GET_GRUPO_ANALISIS_POR_REVISTA,
                             QUERY_GET_ARCHIVO_REVISTA_POR_REVISTA)


from models import Revista, Nota, Autor, Tema, Carta, StaffMiembro, Categoria, ArchivoResumen
from collections import defaultdict
import utils
import logging

logger = logging.getLogger(__name__)

class DBService:

    @staticmethod
    def configuración_inicial():
        try:
            DataBaseConnection.execute_query(QUERY_CONFIGURACION_INICIAL)

        except Exception as e:
            logger.error(f"Error en la configuración incial de la DB: {e}")
            raise

    @staticmethod
    def get_id_ultima_revista_abierta():
        results = None
        try:
            results = DataBaseConnection.execute_query(QUERY_GET_LAST_ID_OPEN)
            return results['ultimo_nrev']

        except Exception as e:
            logger.error(f"Falló la ejecución del SQL get_id_last_open: {e}")


class RevistaServices:

    @staticmethod
    def get_revista(id: int):
        revista = None
        try:
            vs = DataBaseConnection.execute_query(QUERY_GET_REVISTA_POR_ID, params= (id,))
            revista = Revista.desde_dict(vs)
            return revista
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET REVISTA POR ID: {e}")

    @staticmethod
    def cargar_staff_completo(revista: Revista):
        staff_completo = StaffServices.get_staff(revista.id)
        for elemento in staff_completo:
            integrante = StaffMiembro.desde_dict(elemento)
            revista.staff.append(integrante)

    @staticmethod
    def cargar_notas(revista: Revista):
        notas = NotaServices.get_notas(revista.id)
        for elemento in notas:
            nota = Nota.desde_dict(elemento)
            #NotaServices.completar_extras(nota)
            revista.notas.append(nota)
        RevistaServices.completar_extras_full_revista(revista)
        RevistaServices.establecer_estado_de_la_revista(revista)

    @staticmethod
    def completar_extras_full_revista(revista: Revista):
        autores = RevistaServices.get_autores(revista.id)
        RevistaServices.cargar_autores(revista, autores)
        temas = RevistaServices.get_temas(revista.id)
        RevistaServices.cargar_temas(revista, temas)
        grupos = RevistaServices.get_grupos(revista.id)
        RevistaServices.cargar_grupos(revista, grupos)
        archivos_resumen = RevistaServices.get_archivo_resumen(revista.id)
        RevistaServices.cargar_archivo_resumen(revista, archivos_resumen)
        
        
    @staticmethod
    def get_autores(revista_id: int) -> tuple[dict] | None:
        autores_revista = None
        try:
            vs = DataBaseConnection.execute_query(QUERY_GET_AUTORES_POR_REVISTA, params=(revista_id,), select_multiple_results=True)
            autores_revista = vs
            return autores_revista
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY_GET_AUTORES_POR_REVISTA: {e}")

    @staticmethod
    def cargar_autores(revista: Revista, autores: tuple[dict]):
        autores_por_nota= defaultdict(list)
        for a in autores:
            autores_por_nota[a["nota_id"]].append(Autor(a))

        for nota in revista.notas:
            nota.autores = autores_por_nota.get(nota.id, [])

    @staticmethod
    def get_temas(revista_id: int) -> tuple[dict] | None:
        try:
            return DataBaseConnection.execute_query(QUERY_GET_TEMAS_POR_REVISTA, params=(revista_id,), select_multiple_results=True) or []
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY_GET_TEMAS_POR_REVISTA: {e}")
            return []

    @staticmethod
    def cargar_temas(revista: Revista, temas: tuple[dict]):
        temas_por_nota = defaultdict(list)
        for t in temas:
            temas_por_nota[t["nota_id"]].append(Tema(t))

        for nota in revista.notas:
            nota.temas = temas_por_nota.get(nota.id, [])

    @staticmethod
    def get_grupos(revista_id: int) -> tuple[dict] | None:
        try:
            return DataBaseConnection.execute_query(QUERY_GET_GRUPO_ANALISIS_POR_REVISTA, params=(revista_id,), select_multiple_results=True) or []
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY_GET_TEMAS_POR_REVISTA: {e}")
            return []
    
    @staticmethod
    def cargar_grupos(revista: Revista, grupos: tuple[dict]):
        grupos_por_nota = defaultdict(list)
        for g in grupos:
            grupos_por_nota[g["nota_id"]].append(Categoria(g))
        
        for nota in revista.notas:
            nota.categorias = grupos_por_nota.get(nota.id, [])

    @staticmethod
    def get_archivo_resumen(revista_id: int) -> tuple[dict] | None:
        try:
            return DataBaseConnection.execute_query(QUERY_GET_ARCHIVO_REVISTA_POR_REVISTA, params=(revista_id,), select_multiple_results=True) or []
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY_GET_AUTORES_POR_REVISTA: {e}")
            return []

    @staticmethod
    def cargar_archivo_resumen(revista: Revista, archivos_resumen: tuple[dict]):
        archivo_por_nota= defaultdict(list)
        for a in archivos_resumen:
            archivo_por_nota[a["nota_id"]].append(ArchivoResumen(a))

        for nota in revista.notas:
            nota.archivos = archivo_por_nota.get(nota.id,)


    @staticmethod
    def cargar_correo(revista: Revista):
        correo = CartaServices.get_cartas(revista.id)
        for elemento in correo:
            carta = Carta.desde_dict(elemento)
            #CartaServices.cargar_archivo_resumen(carta)
            #CartaServices.cargar_grupo_analisis(carta)
            revista.correo.append(carta)


    @staticmethod
    def establecer_estado_de_la_revista(revista: Revista):
        if revista.formato == "M":
            revista.estado = "missing"
        elif len(revista.notas) == 0:
            revista.estado = "pendiente"
        else:
            revista.estado = "cargado"

    @staticmethod
    def cargar_hexagrama(revista: Revista):
        revista.hexagrama.codigo_binario = utils.get_binario_hexagrama(revista.hexagrama.numero)
        revista.hexagrama.lineas = utils.get_lineas_hexagrama(revista.hexagrama.codigo_binario)

    @staticmethod
    def guardar_cambios_revista(id_revista, datos_actualizados: dict):
        parametros = (
            datos_actualizados['tapa'],
            datos_actualizados['nota_tapa'],
            datos_actualizados['hexagrama'],
            datos_actualizados['paginas_faltantes'],
            datos_actualizados['formato_en_archivo'],
            datos_actualizados['comentarios'],
            datos_actualizados['precio_nominal'],
            id_revista)
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_UPDATE_REVISTA_POR_ID, parametros)
            logger.info(f"Modificaciones en revista realizadas: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY UPDATE REVISTA POR ID: {e}")


class StaffServices:

    @staticmethod
    def get_staff(id_revista: int):
        staff_completo = None
        try:
            staff_completo = DataBaseConnection.execute_query(QUERY_GET_STAFF_POR_ID_REVISTA, params= (id_revista,), select_multiple_results=True)
            return staff_completo
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET STAFF POR ID: {e}")


class NotaServices:

    @staticmethod
    def get_notas(id_revista: int):
        notas = None
        try:
            notas = DataBaseConnection.execute_query(QUERY_GET_NOTAS_POR_ID_REVISTA, params= (id_revista,), select_multiple_results=True)
            return notas
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET NOTAS POR ID_REVISTA: {e}")

    @staticmethod
    def completar_extras(nota: Nota):
        NotaServices.cargar_autores(nota)
        NotaServices.cargar_temas(nota)
        NotaServices.cargar_categorias(nota)
        NotaServices.cargar_archivo_resumen(nota)
        return nota

    @staticmethod
    def get_nota_por_id_nota(id_nota: int):
        nota = None
        try:
            nota = DataBaseConnection.execute_query(QUERY_GET_NOTA_POR_ID_NOTA, params= (id_nota,))
            return nota
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET NOTA POR ID_NOTA: {e}")

    @staticmethod
    def get_autor_de_nota(id_nota: int):
        autores = None
        try:
            autores = DataBaseConnection.execute_query(QUERY_GET_AUTOR_DE_NOTA_POR_NOTA_ID, params=(id_nota,), select_multiple_results=True)
            return autores
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET AUTOR DE NOTA POR NOTA_ID: {e}")

    @staticmethod
    def cargar_autores(nota: Nota):
        autores = NotaServices.get_autor_de_nota(nota.id)
        for elemento in autores:
            autor = Autor.desde_dic(elemento)
            nota.autores.add(autor)

    @staticmethod
    def cargar_categorias(nota: Nota):
        categorias = NotaServices.get_categorias(nota.id)
        for elemento in categorias:
            categoria = Categoria.desde_dict(elemento)
            nota.categorias.add(categoria)

    @staticmethod
    def get_categorias(nota_id: int):
        categorias = None
        try:
            categorias = DataBaseConnection.execute_query(QUERY_GET_CATEGORIAS_POR_NOTA_ID, (nota_id,), select_multiple_results=True)
            return categorias
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET CATEGORIAS POR NOTA_ID: {e}")

    @staticmethod
    def cargar_archivo_resumen(nota: Nota):
        archivos = NotaServices.get_archivo_resumen(nota.id)
        for elemento in archivos:
            archivo = ArchivoResumen.desde_dict(elemento)
            nota.analisis.append(archivo)

    @staticmethod
    def get_archivo_resumen(nota_id: int):
        archivos = None
        try:
            archivos = DataBaseConnection.execute_query(QUERY_GET_ARCHIVO_RESUMEN_POR_NOTA_ID, params=(nota_id,), select_multiple_results=True)
            return archivos or {}
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET ARCHIVO RESUMEN POR NOTA_ID: {e}")

    @staticmethod
    def get_temas_de_nota(id_nota: int):
        temas = None
        try:
            temas = DataBaseConnection.execute_query(QUERY_GET_TEMAS_DE_NOTA_POR_NOTA_ID, params=(id_nota,), select_multiple_results=True)
            return temas
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET TEMAS DE NOTA POR NOTA_ID: {e}")

    @staticmethod
    def cargar_temas(nota: Nota):
        temas = NotaServices.get_temas_de_nota(nota.id)
        for elemento in temas:
            tema = Tema.desde_dict(elemento)
            nota.temas.add(tema)

    @staticmethod
    def get_autores_en_una_linea(nota: Nota):
        linea = ""
        for i, autor in enumerate(nota.autores, start=1):
            if i == len(nota.autores):
                linea += utils.get_nombre_completo(autor)
            else:
                linea += utils.get_nombre_completo(autor) + "; "
        return linea


class CartaServices:

    @staticmethod
    def get_cartas(id_revista: int):
        correo = None
        try:
            correo = DataBaseConnection.execute_query(QUERY_GET_CARTAS_POR_REVISTA_ID, params=(id_revista,), select_multiple_results=True)
            return correo
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET CARTAS POR REVISTA_ID: {e}")

    @staticmethod
    def cargar_archivo_resumen(carta: Carta):
        tabla_archivos_resumenes = CartaServices.get_archivo_resumen_de_carta_por_id_carta(carta.id)
        for elemento in tabla_archivos_resumenes:
            carta.archivo_resumen.append(elemento)

    @staticmethod
    def cargar_grupo_analisis(carta: Carta):
        grupo_analisis = CartaServices.get_grupo_analisis(carta.id)
        carta.categoria_analisis = grupo_analisis

    @staticmethod
    def get_grupo_analisis(carta_id: int):
        categorias = []
        try:
            tabla = DataBaseConnection.execute_query(QUERY_GET_GRUPOS_ANALISIS_PARA_CARTA, params=(carta_id,), select_multiple_results=True)
            for elemento in tabla:
                carga = Categoria.desde_dict(elemento)
                categorias.append(carga)

            return categorias
        except Exception as e:
            logger.error(f"Falló la ejecución de la query GET GRUPOS ANALISIS PARA CARTA")

    @staticmethod
    def get_archivo_resumen_de_carta_por_id_carta(carta_id):
        archivo_resumen = []
        try:
            tabla = DataBaseConnection.execute_query(QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID_CARTA, params=(carta_id,), select_multiple_results=True)
            if tabla:
                for reg in tabla:
                    carga = ArchivoResumen.desde_dict(reg)
                    archivo_resumen.append(carga)
            return archivo_resumen
        except Exception as e:
            logger.error(f"Falló la ejecución de la QUERY GET ARCHIVO RESUMEN POR ID")

    @staticmethod
    def borrar_archivo_resumen_en_carta(id_analisis: int):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_DELETE_ARCHIVO_RESUMEN_CARTA, params=(id_analisis,))
            logger.info(f"Se ha eliminado el archivo resumen correspondiente a la carta: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la eliminación del archivo resumen de la carta: {e}")

    @staticmethod
    def actualizar_titulo_de_archivo_resumen(id_analisis: int, titulo: str):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_ACTUALIZAR_TITULO_ARCHIVO_RESUMEN_CARTA, params=(titulo, id_analisis))
            logger.info(f"Se ha actualizado el título de un arcihvo resumen: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló el query ACTUALIZAR TITULO DE ARCHIVO RESUMEN EN CARTA: {e}")

    @staticmethod
    def guardar_nueva_carta(carta: dict, revista_id):
        relevante = 1 if carta['relevante'] else 0
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_GUARDAR_NUEVA_CARTA, params=(revista_id, carta['remitente'], carta['tema'], relevante))
            logger.info(f"Se ha guardado una nueva carta_ {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló el query AGREGAR NUEVA CARTA: {e}")

    @staticmethod
    def actualizar_carta(carta: dict):
        relevante = 1 if carta['relevante'] else 0
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_UPDATE_CARTA, params=(carta['remitente'], carta['tema'], relevante, carta["id"]))
            logger.info(f"Se ha actualizado una carta: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la querry UPDATE CARTA")

    @staticmethod
    def agregar_carta_a_grupo_de_analisis(carta_id, grupo_id):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_ADD_CARTA_A_GRUPO_ANALISIS, params=(carta_id, grupo_id))
            logger.info(f"Se ha agregado una carta a un grupo de análisis: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la query ADD CARTA: {e}")

    @staticmethod
    def quitar_carta_del_grupo_de_analisis(carta_id, grupo_id):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_DELETE_CARTA_DE_GRUPO_ANALISIS, params=(carta_id, grupo_id))
            logger.info(f"Se ha quitado una carta del grupo de análisis: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la query Quitar Carta del grupo de análisis: {e}")


class AutorServices:

    @staticmethod
    def get_lista_autores_por_nombre(nombre: str):
        autores = None
        try:
            nombre_con_comodines = f"%{nombre}%"
            autores = DataBaseConnection.execute_query(QUERY_GET_AUTORES_POR_NOMBRE, params=(nombre_con_comodines,), select_multiple_results=True)
            return autores
        except Exception as e:
            logger.error(f"Falló la ejecucion sql QUERY GET AUTORES POR NOMBRE: {e}")

    @staticmethod
    def get_autor_por_id_autor(id_autor: int):
        autor = None
        try:
            autor = DataBaseConnection.execute_query(QUERY_GET_AUTOR_POR_ID_NOMBRE, params=(id_autor,), select_multiple_results=False)
            return autor
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET AUTOR POR ID_NOMBRE: {e}")

    @staticmethod
    def get_notas_de_autor(id_autor: int):
        notas = None
        try:
            notas = DataBaseConnection.execute_query(QUERY_GET_NOTAS_POR_AUTOR, (id_autor,), True)
            return notas
        except Exception as e:
            logger.error(f"Falló la ejecución sql QUERY GET NOTAS DE AUTOR")

    @staticmethod
    def guardar_cambios_autor(id_autor, datos_actualizados: dict):
        parametros = (
            datos_actualizados['nombre'],
            datos_actualizados['apellido'],
            datos_actualizados['genero'],
            datos_actualizados['comentarios'],
            id_autor
        )
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_UPDATE_AUTOR, parametros)
            logger.info(f"Modificaciones realizadas en autor: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la ejecución de QUERRY UPDATE AUTOR: {e}")

class TemaServices:

    @staticmethod
    def get_temas_busqueda(busqueda: str = ""):

        try:
            busqueda_con_comodines = f"%{busqueda}%"
            temas = DataBaseConnection.execute_query(QUERY_GET_TEMAS_POR_TEMA, (busqueda_con_comodines,), True)
            return temas
        except Exception as e:
            logger.error(f"Falló la ejecución de GET TEMAS POR TEMAS: {e}")

    @staticmethod
    def get_temas_segun_tags_seleccionados(busqueda: str, id_notas: list):
        sql_query = QUERY_BASE_TEMAS_POR_NOTAS
        parametros = (f"%{busqueda}%",)
        for id_nota in id_notas:
            parametros += (id_nota,)

        for i, par in enumerate(parametros):
            if i > 1:
                sql_query += " OR nt.nota_id = %s"
        sql_query += ") ORDER BY t.tema;"

        try:
            temas = DataBaseConnection.execute_query(sql_query, params=parametros, select_multiple_results=True)
            return temas
        except Exception as e:
            logger.error(f"Falló la ejecución de GET TEMAS SEGUN TAGS SELECCIONADOS DINAMICO: {e}")

    @staticmethod
    def get_notas_por_temas_seleccionados(tags: list[Tema]):
        sql_query = QUERY_BASE_NOTAS_POR_TEMAS
        parametros = []
        for tag in tags:
            parametros.append(tag.id)

        parametros = tuple(parametros)
        n_parametros = len(parametros)

        if n_parametros:
            for i, tag in enumerate(parametros, start=1):
                if i > 1:
                    sql_query += ", %s"

            sql_query += f"""
                )
                GROUP BY n.id
                HAVING COUNT(DISTINCT nt.tema_id) = {n_parametros};
            """

            try:
                notas = DataBaseConnection.execute_query(sql_query, params=parametros, select_multiple_results=True)
                return notas
            except Exception as e:
                logger.error(f"Falló la ejecución de GET NOTAS POR TEMAS DINAMICO: {e}")
        else:
            return []


class AnalisisService:

    @staticmethod
    def get_grupos_analisis():
        categorias = []
        try:
            grupos = DataBaseConnection.execute_query(QUERY_GET_GRUPOS_ANALISIS, select_multiple_results=True)
            for elemento in grupos:
                carga = Categoria.desde_dict(elemento)
                categorias.append(carga)
            return categorias

        except Exception as e:
            logger.error(f"Falló la ejecución de GET GRUPOS ANALISIS: {e}")

    @staticmethod
    def agregar_grupo_analisis(nombre: str):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_AGREGAR_GRUPO_ANALISIS, params=(nombre,))
            logger.info(f"Consulta Agregar grupo análisis ejecutada: filas modificadas {filas_afectadas}")
        except Exception as e:
            logger.error(f"Falló la ejecución de la query AGREGAR GRUPO ANALISIS: {e}")

    @staticmethod
    def get_notas_por_grupo_analisis(id_grupo: int):
        notas = None
        try:
            notas = DataBaseConnection.execute_query(QUERY_GET_NOTAS_POR_GRUPO_ANALISIS, params=(id_grupo,), select_multiple_results=True)
            return notas
        except Exception as e:
            logger.error(f"Falló la ejecución de la query GET NOTAS POR GRUPO ANALISIS: {e}")

    @staticmethod
    def get_cartas_por_grupo_analisis(id_grupo: int):
        notas = None
        try:
            notas = DataBaseConnection.execute_query(QUERY_GET_CARTAS_POR_GRUPO_ANALISIS, params=(id_grupo,), select_multiple_results=True)
            return notas
        except Exception as e:
            logger.error(f"Falló la ejecución de la query GET NOTAS POR GRUPO ANALISIS: {e}")

    @staticmethod
    def cargar_nota_en_grupo_de_analisis(nota_id: int, grupo_id: int):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_CARGAR_NOTA_AL_GRUPO_ANALISIS, params=(nota_id, grupo_id))
            logger.info(f"Consulta Agregar nota a grupo de análisis ejecutada: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Falló la ejecución query de Agregar nota a grupo de análisis: {e}")

    @staticmethod
    def comprobar_si_nota_ya_existe_en_grupo_analisis (nota_id: int, grupo_id:int):
        notas = AnalisisService.get_notas_por_grupo_analisis(grupo_id)
        for nota in notas:
            if nota['id'] == nota_id:
                return True
        return False

    @staticmethod
    def quitar_nota_de_grupo_de_analisis (nota_id: int, grupo_id: int):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_DELETE_NOTA_DE_GRUPO_DE_ANALISIS, params=(nota_id, grupo_id))
            logger.info(f"Se ha quitado la nota seleccionada del agrupamiento: {filas_afectadas} filas afectadas en DB")
        except Exception as e:
            logger.error(f"Error al ejecutar la query QUITAR NOTA DE AGRUPAMIENTO: {e}")


class ServicesArchivoResumen:

    @staticmethod
    def agregar_archivo_resumen(nota_id: int, cuerpo_texto: str, titulo: str):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_AGREGAR_ARCHIVO_RESUMEN, params=(nota_id, cuerpo_texto, titulo))
            logger.info(f"Se ha agregado un archivo resumen: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Error al ejecutar la query AGREGAR ARCHIVO RESUMEN: {e}")

    @staticmethod
    def agregar_archivo_resumen_carta(carta_id: int, cuerpo_texto: str, titulo: str):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_AGREGAR_ARCHIVO_RESUMEN_CARTA, params=(carta_id, cuerpo_texto, titulo))
            logger.info(f"Se ha agregado un archivo resumen para carta: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Error al ejecutar la QUERY AGREGAR ARCHIVO RESUMEN EN CARTA: {e}")

    @staticmethod
    def modificar_archivo_resumen(id_analisis, cuerpo_texto, titulo):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_MODIFICAR_ARCHIVO_RESUMEN, params=(cuerpo_texto, titulo, id_analisis))
            logger.info(f"Se ha modificado el archivo resumen: {filas_afectadas} una fila afectada en la DB")
        except Exception as e:
            logger.error(f"Error al ejecutar la query MODIFICAR ARCHIVO RESUMEN: {e}")

    @staticmethod
    def modificar_archivo_resumen_carta(id_analisis, cuerpo_texto, titulo):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_MODIFICAR_ARCHIVO_RESUMEN_CARTA, params=(cuerpo_texto, titulo, id_analisis))
            logger.info(f"Se ha modificado el archivo resumen de carta: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Error al ejectuar la query MODIFICAR ARCHIVO RESUMEN PARA CARTA: {e}")

    @staticmethod
    def get_archivo_resumen_por_id(analisis_id):
        try:
            archivo_resumen = DataBaseConnection.execute_query(QUERY_GET_ARCHIVO_RESUMEN, params=(analisis_id,))
            return archivo_resumen
        except Exception as e:
            logger.error(f"Error al ejecutar la query MODIFICAR ARCHIVO RESUMEN: {e}")

    @staticmethod
    def get_archivo_resumen_carta_por_id(analisis_id):
        try:
            archivo_resumen = DataBaseConnection.execute_query(QUERY_GET_ARCHIVO_RESUMEN_CARTA_POR_ID, params=(analisis_id,))
            return archivo_resumen
        except Exception as e:
            logger.error(f"Error al ejecutar la query get archivo resumen carta por id: {e}")

    @staticmethod
    def get_archivo_resumen_listo(analisis_id):
        diccionario = ServicesArchivoResumen.get_archivo_resumen_por_id(analisis_id)
        archivo = ArchivoResumen.desde_dict(diccionario)
        return archivo

    @staticmethod
    def get_archivo_resumen_carta_listo(analisis_id):
        diccionario = ServicesArchivoResumen.get_archivo_resumen_carta_por_id(analisis_id)
        archivo = ArchivoResumen.desde_dict(diccionario)
        return archivo


    @staticmethod
    def delete_archivo_resumen_por_id(analisis_id):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_DELETE_ARCHIVO_RESUMEN, params=(analisis_id,))
            logger.info(f"Se ha borrado el archivo resumen en la base de datos: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Ha habido un error al ejecutar la query DELETE ARCHIVO RESUMEN: {e}")

    @staticmethod
    def actualizar_titulo(analisis_id: int, titulo: str):
        try:
            filas_afectadas = DataBaseConnection.execute_query(QUERY_ACTUALIZAR_TITULO, params=(titulo, analisis_id))
            logger.info(f"Se ha cambiado el título del archivo resumen: {filas_afectadas} filas afectadas")
        except Exception as e:
            logger.error(f"Ha habido un error al ejecutar la query ACTUALIZAR TITULO: {e}")