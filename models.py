from dataclasses import dataclass
import datetime

class Autor:

    def __init__(self, autor: dict):
        self.id: int = autor['id']
        self.nombre: str = autor['nombre']
        self.apellido: str = autor['apellido']
        self.genero: str = autor['genero']
        self.comentarios: str = autor['comentarios']


class Carta:

    def __init__(self, carta: dict):
        self.id: int = carta['id']
        self.revista: int = carta['revista_id']
        self.remitente: str = carta['remitente']
        self.tema: str = carta['tema']
        self.relevante: bool = carta['relevante']
        self.categoria_analisis: set = set()
        self.archivo_resumen: set = set()


class Hexagrama:

    def __init__(self, numero: int):
        self.numero: int = numero
        self.lineas: str = None
        self.codigo_binario: str = None


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
        self.id: int = numero['id']
        ano, mes, dia = map(int, str(numero['fecha']).split("-"))
        self.fecha: datetime.datetime = datetime.datetime(ano, mes, dia)
        self.tapa: str = numero['tapa']
        self.nota_tapa: str = numero['nota_de_tapa']
        self.hexagrama: int = Hexagrama(numero['hexagrama'])
        self.paginas_faltantes: str = numero['paginas_faltantes']
        self.formato: str = numero['formato_en_archivo']
        self.comentarios: str = numero['comentarios']
        self.precio: str = numero['precio_nominal'] if numero['precio_nominal'] else ""
        self.staff: list[StaffMiembro] = []
        self.notas: list[Nota] = []
        self.correo: list[Carta] = []
        self.estado:str = None

    def buscar_nota_por_id(self, id: int):
        for n in self.notas:
            if n.id == id:
                return n
        return None

class StaffMiembro:

    def __init__(self, staff_miembro):
        self.posicion: str = staff_miembro["posicion"]
        self.nombre: str = staff_miembro["nombre"]
        self.apellido: str = staff_miembro["apellido"]
        self.genero:str = staff_miembro["genero"]


class Tema:

    def __init__(self, tema: dict):
        self.id: int = tema['id']
        self.tema: str = tema['tema']

class Categoria:

    def __init__(self, categoria: dict):
        self.id: int = categoria['id']
        self.categoria: str = categoria['grupo']

class ArchivoResumen:

    def __init__(self, analisis: dict):
        self.id:int = analisis['id']
        self.parent_id: int = analisis.get("nota_id") or analisis.get("carta_id")
        self.titulo: str = analisis['titulo']
        self.cuerpo_texto: str = analisis['cuerpo_texto']