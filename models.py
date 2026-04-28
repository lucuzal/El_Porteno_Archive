from dataclasses import dataclass
import datetime

class Autor:

    def __init__(self, autor: dict):
        self.id = autor['id']
        self.nombre = autor['nombre']
        self.apellido = autor['apellido']
        self.genero = autor['genero']
        self.comentarios = autor['comentarios']


class Carta:

    def __init__(self, carta: dict):
        self.id = carta['id']
        self.revista = carta['revista_id']
        self.remitente = carta['remitente']
        self.tema = carta['tema']
        self.relevante = carta['relevante']
        self.categoria_analisis = []
        self.archivo_resumen = []


class Hexagrama:

    def __init__(self, numero: int):
        self.numero = numero
        self.lineas = None
        self.codigo_binario = None


class Nota:

    def __init__(self, nota: dict):
        self.id: int = nota['id']
        self.revista: int = nota['revista_id']
        self.titulo: str = nota['titulo']
        self.paginas: str = nota['paginas']
        self.dossier: str = nota['dossier']
        self.seccion: str = nota['seccion']
        self.tipo: str = nota['tipo']
        self.original: bool = nota['original']
        self.relacionado: bool = nota['relevante']
        self.relacionado_sexualidad: bool = nota['relevante_sexualidad']
        self.relacionado_memoria: bool = nota['relevante_testimonio']
        self.comentarios: str = nota['comentarios']
        self.autores: set = set()
        self.temas: set = set()
        self.categorias: set = set()
        self.analisis: set = set()


class Revista:

    def __init__(self, numero: dict):
        self.id = numero['id']
        ano, mes, dia = map(int, str(numero['fecha']).split("-"))
        self.fecha = datetime.datetime(ano, mes, dia)
        self.tapa = numero['tapa']
        self.nota_tapa = numero['nota_de_tapa']
        self.hexagrama = Hexagrama(numero['hexagrama'])
        self.paginas_faltantes = numero['paginas_faltantes']
        self.formato = numero['formato_en_archivo']
        self.comentarios = numero['comentarios']
        self.precio = numero['precio_nominal'] if numero['precio_nominal'] else ""
        self.staff: list[StaffMiembro] = []
        self.notas: list[Nota] = []
        self.correo: list[Carta] = []
        self.estado = None

    def buscar_nota_por_id(self, id: int):
        for n in self.notas:
            if n.id == id:
                return n
        return None

class StaffMiembro:

    def __init__(self, staff_miembro):
        self.posicion = staff_miembro["posicion"]
        self.nombre = staff_miembro["nombre"]
        self.apellido = staff_miembro["apellido"]
        self.genero = staff_miembro["genero"]


class Tema:

    def __init__(self, tema: dict):
        self.id = tema['id']
        self.tema = tema['tema']

class Categoria:

    def __init__(self, categoria: dict):
        self.id = categoria['id']
        self.categoria = categoria['grupo']

class ArchivoResumen:

    def __init__(self, analisis: dict):
        self.id = analisis['id']
        self.parent_id = analisis.get("nota_id") or analisis.get("carta_id")
        self.titulo = analisis['titulo']
        self.cuerpo_texto = analisis['cuerpo_texto']