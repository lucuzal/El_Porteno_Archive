from datetime import date

class Autor:

    def __init__(self, nombre: str, apellido: str, genero: str, comentarios: str, id: int = None):
        self.id: int = id
        self.nombre: str = nombre
        self.apellido: str = apellido
        self.genero: str = genero
        self.comentarios: str = comentarios
        
    @classmethod
    def desde_dic(cls, autor: dict):
        return cls(id = autor['id'],
                    nombre = autor['nombre'],
                    apellido = autor['apellido'],
                    genero = autor['genero'],
                    comentarios = autor['comentarios'])


    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0],
                   nombre = fila[1],
                   apellido = fila[2],
                   genero = fila[3],
                   comentarios = fila[4])
    
    def nombre_completo(self, apellido_primero: bool = False) -> str:
        if not self.nombre == "":
            if not apellido_primero:
                return f"{self.nombre} {self.apellido}"
            else:
                return f"{self.apellido}, {self.nombre}"
        else:
            return self.apellido


class Carta:

    def __init__(self, id:int, revista_id:int, remitente:str, tema:str, relevante:bool, categoria_analisis: set = None, archivo_resumen: set = None):
        self.id: int = id
        self.revista: int = revista_id
        self.remitente: str = remitente
        self.tema: str = tema
        self.relevante: bool = relevante
        self.categoria_analisis: set[Categoria] = categoria_analisis if categoria_analisis is not None else set()
        self.archivo_resumen: set[ArchivoResumen] = archivo_resumen if archivo_resumen is not None else set()

    @classmethod
    def desde_dict(cls, carta:dict):
        return cls(id = carta['id'],
                   revista_id = carta['revista_id'], 
                   remitente = carta['remitente'], 
                   tema = carta['tema'], 
                   relevante = carta['relevante'])
    
    @classmethod
    def desde_sql(cls, fila:tuple):
        return cls(id = fila[0],
                   revista_id = fila[1], 
                   remitente = fila[2], 
                   tema = fila[3], 
                   relevante = fila[4])


class Hexagrama:

    def __init__(self, numero: int, lineas: str = None, codigo_binario: str = None):
        self.numero: int = numero
        self.lineas: str = lineas
        self.codigo_binario: str = codigo_binario


class Nota:

    def __init__(self, id: int, revista_id: int, titulo: str, paginas: str, dossier:str, seccion:str, tipo:str,
                 original: bool, relacionado: bool, relacionado_sexualidad: bool, relacionado_memoria: bool, comentarios: str,
                 autores: set = None, temas: set = None, categorias: set = None, analisis: set = None):
        self.id: int = id
        self.revista: int = revista_id
        self.titulo: str = titulo
        self.paginas: str = paginas
        self.dossier: str = dossier
        self.seccion: str = seccion
        self.tipo: str = tipo
        self.original: bool = original
        self.relacionado: bool = relacionado
        self.relacionado_sexualidad: bool = relacionado_sexualidad
        self.relacionado_memoria: bool = relacionado_memoria
        self.comentarios: str = comentarios
        self.autores: set[Autor] = autores if autores is not None else set()
        self.temas: set[Tema] = temas if temas is not None else set()
        self.categorias: set[Categoria] = categorias if categorias is not None else set()
        self.analisis: set[ArchivoResumen] = analisis if analisis is not None else set()
    
    @classmethod
    def desde_dict(cls, nota: dict):
        return cls(id = nota['id'], 
                   revista_id = nota['revista_id'], 
                   titulo = nota['titulo'], 
                   paginas = nota['paginas'], 
                   dossier = nota['dossier'], 
                   seccion = nota['seccion'], 
                   tipo = nota['tipo'], 
                   original = nota['original'], 
                   relacionado = nota['relevante'], 
                   relacionado_sexualidad = nota['relevante_sexualidad'], 
                   relacionado_memoria = nota['relevante_testimonio'], 
                   comentarios = nota['comentarios'])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0], 
                   revista_id = fila[1], 
                   titulo = fila[2], 
                   paginas = fila[3], 
                   dossier = fila[4], 
                   seccion = fila[5], 
                   tipo = fila[6], 
                   original = fila[7], 
                   relacionado = fila[8], 
                   relacionado_sexualidad = fila[9], 
                   relacionado_memoria = fila[10], 
                   comentarios = fila[11])

    def buscar_nota_por_id(self, id: int):
        for n in self.notas:
            if n.id == id:
                return n
        return None
    
    def to_dict(self) -> dict:
        diccionario = {"id": self.id,
                       "titulo": self.titulo,
                       "paginas": self.paginas,
                       "dossier": self.dossier,
                       "seccion": self.seccion,
                       "tipo": self.tipo,
                       "original": self.original,
                       "relacionado": self.relacionado,
                       "relacionado_sexualidad": self.relacionado_sexualidad,
                       "relacionado_memoria": self.relacionado_memoria,
                       "comentarios": self.comentarios,
                       "autores": self.autores,
                       "temas": self.temas,
                       "categorias": self.categorias,
                       "analisis": self.analisis}
        return diccionario


class StaffMiembro:

    def __init__(self, posicion: str, nombre: str, apellido: str, genero:str):
        self.posicion: str = posicion
        self.nombre: str = nombre
        self.apellido: str = apellido
        self.genero:str = genero
    
    @classmethod
    def desde_dict(cls, staff_miembro: dict):
        return cls(posicion = staff_miembro["posicion"], 
                   nombre = staff_miembro["nombre"], 
                   apellido = staff_miembro["apellido"], 
                   genero = staff_miembro["genero"])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(posicion = fila[0], 
                   nombre = fila[1], 
                   apellido = fila[2], 
                   genero = fila[3])
    
    def nombre_completo(self, apellido_primero: bool = False) -> str:
        if not self.nombre == "":
            if not apellido_primero:
                return f"{self.nombre} {self.apellido}"
            else:
                return f"{self.apellido}, {self.nombre}"
        else:
            return self.apellido


class Revista:

    def __init__(self, id: int, fecha: str, tapa: int, nota_tapa: str, hexagrama: int, paginas_faltantes: str,
                 formato: str, comentarios: str, precio: str = None, staff: list[StaffMiembro] = None, notas: list[Nota] = None,
                 correo: list[Carta] = None, estado: str = None) :
        self.id: int = id
        ano, mes, dia = map(int, str(fecha).split("-"))
        self.fecha: date = date(ano, mes, dia)
        self.tapa: str = tapa
        self.nota_tapa: str = nota_tapa
        self.hexagrama: Hexagrama = Hexagrama(hexagrama)
        self.paginas_faltantes: str = paginas_faltantes
        self.formato: str = formato
        self.comentarios: str = comentarios
        self.precio: str = precio if precio else ""
        self.staff: list[StaffMiembro] = staff if staff is not None else list()
        self.notas: list[Nota] = notas if notas is not None else list()
        self.correo: list[Carta] = correo if correo is not None else list()
        self.estado:str = estado

    @classmethod
    def desde_dict(cls, numero: dict):
        return cls(id = numero['id'], 
                   fecha = numero['fecha'], 
                   tapa = numero['tapa'], 
                   nota_tapa = numero['nota_de_tapa'], 
                   hexagrama = numero['hexagrama'],
                   paginas_faltantes = numero['paginas_faltantes'],
                   formato = numero['formato_en_archivo'],
                   comentarios = numero['comentarios'],
                   precio = numero['precio_nominal'])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0], 
                   fecha = fila[1], 
                   tapa = fila[2], 
                   nota_tapa = fila[3], 
                   hexagrama = fila[4],
                   paginas_faltantes = fila[5],
                   formato = fila[6],
                   comentarios = fila[7],
                   precio = fila[8])

    def buscar_nota_por_id(self, id: int) -> Nota | None:
        return next((n for n in self.notas if n.id == id), None)


class Tema:

    def __init__(self, tema: str, id: int = None):
        self.id: int = id
        self.tema: str = tema

    @classmethod
    def desde_dict(cls, tema: dict):
        return cls(id = tema['id'], tema = tema['tema'])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0], tema = fila[1])


class Categoria:

    def __init__(self, id: int, categoria: str):
        self.id: int = id
        self.categoria: str = categoria

    @classmethod
    def desde_dict(cls, categoria: dict):
        return cls(id = categoria['id'], categoria = categoria['grupo'])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0], categoria = fila[1])


class ArchivoResumen:

    def __init__(self, id: int, parent_id: int, titulo: str, cuerpo_texto: str):
        self.id:int = id
        self.parent_id: int = parent_id
        self.titulo: str = titulo
        self.cuerpo_texto: str = cuerpo_texto

    @classmethod
    def desde_dict(cls, analisis: dict):
        return cls(id = analisis['id'], 
                   parent_id = analisis.get("nota_id") or analisis.get("carta_id"), 
                   titulo = analisis['titulo'], 
                   cuerpo_texto = analisis['cuerpo_texto'])

    @classmethod
    def desde_sql(cls, fila: tuple):
        return cls(id = fila[0], 
                   parent_id = fila[1], 
                   titulo = fila[2], 
                   cuerpo_texto = fila[3])