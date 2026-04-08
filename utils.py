

from config import config
from models import Autor, StaffMiembro, Nota, Tema, Categoria, Carta
from typing import Union
from datetime import datetime
from gi.repository import Gtk
from html.parser import HTMLParser
from services import CartaServices
import html


#Config. GTK

def get_binario_hexagrama(numero_hexagrama: int):
    columna = f"h{numero_hexagrama}"
    binario = config.HEXAGRAMA[columna]
    return binario

def get_lineas_hexagrama(binario_hexagrama: str):
    lineas = ""
    for l in binario_hexagrama:
        lineas += "____________\n" if l == "1" else "_____  _____\n"

    return lineas

def get_nombre_completo(persona: Union[Autor, StaffMiembro], apellido_primero: bool = False):
    if apellido_primero:
        if persona.nombre == "":
            return persona.apellido
        else:
            return f"{persona.apellido}, {persona.nombre}"
    else:
        if persona.nombre == "":
            return persona.apellido
        else:
            return f"{persona.nombre} {persona.apellido}"

def changes_were_made(original: dict, final: dict):

    return False if original == final else True

    def cargar_texto(self, fecha: datetime):
        texto = fecha.strftime("%B").upper() + " " + str(fecha.year)
        self._texto = texto

def formato_fecha(fecha: datetime, formato: str = "entera_digitos"):
    texto = None
    if formato == "entera_digitos":
        texto = fecha.strftime("%Y.%m.%d")
    elif formato == "mes":
        texto = fecha.strftime("%B").title()
    elif formato == "entera_visor":
        texto = fecha.strftime("%B").upper() + " " + str(fecha.year)
    elif formato == "año":
        texto = str(fecha.year)
    return texto

def to_nota(lista_notas: list[dict]):
    from services import NotaServices
    notas = []
    if lista_notas:
        for elemento in lista_notas:
            carga = Nota(elemento)
            NotaServices.completar_extras(carga)
            notas.append(carga)
    return notas

def to_tema(lista_temas: list[dict]):
    temas = []
    for elemento in lista_temas:
        carga = Tema(elemento)
        temas.append(carga)
    return temas

def to_cartas(lista_cartas: list[dict]):
    cartas = []
    for elemento in lista_cartas:
        carga = Carta(elemento)
        CartaServices.cargar_archivo_resumen(carga)
        cartas.append(carga)
    return cartas

def is_in_tags(tema: Tema, lista_temas: list[Tema]):
    for elemento in lista_temas:
        if (tema.id == elemento.id) and (tema.tema == elemento.tema):
            return True
    return False

def press_button(widget):
    if widget.get_active():
        widget.set_active(False)
    else:
        widget.set_active(True)


_COLOR_HEX = {
    "red": "#ff6b6b",
    "orange": "#ffa500",
    "yellow": "#ffd166",
}

def buffer_to_html(text_buffer: Gtk.TextBuffer, tag_map: dict):

    rev = {v: k for k, v in tag_map.items()}

    start, end = text_buffer.get_bounds()
    it = start.copy()

    out_parts = []
    stack = []

    def open_tag(name):
        if name == "bold":
            return "<b>"
        if name == "italic":
            return "<i>"
        if name in _COLOR_HEX:
            return f'<span style="color:{_COLOR_HEX[name]}">'
        return  ""

    def close_tag(name):
        if name in _COLOR_HEX:
            return "</span>"
        if name == "bold":
            return "</b>"
        if name == "italic":
            return "</i>"
        return ""

    ORDER = ("bold", "italic", "red", "orange", "yellow")

    while it.compare(end) < 0:
        ch = it.get_char()
        tags_here = set()
        for t in it.get_tags():
            name = rev.get(t)
            if name:
                tags_here.add(name)

        while stack and stack[-1] not in tags_here:
            top = stack.pop()
            out_parts.append(close_tag(top))

        for name in ORDER:
            if name in tags_here and name not in stack:
                out_parts.append(open_tag(name))
                stack.append(name)

        if ch == "\n":
            out_parts.append("<br/>")
        else:
            out_parts.append(html.escape(ch))

        it.forward_char()

    while stack:
        out_parts.append(close_tag(stack.pop()))

    return "".join(out_parts)

class HTMLToSegmentsParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.segments = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag in ("b", "strong"):
            self.stack.append("bold")
        elif tag in ("i", "em"):
            self.stack.append("italic")
        elif tag == "span":
            style = None
            for (n, v) in attrs:
                if n.lower() == "style":
                    style = v
                    break
            if style:
                parts = [p.strip() for p in style.split(";") if p.strip()]
                for p in parts:
                    if p.startswith("color"):
                        _, val = p.split(":", 1)
                        color = val.strip().lower()
                        for name, hexc in _COLOR_HEX.items():
                            if color == hexc:
                                self.stack.append(name)
                                break
                        break
        elif tag == "br" :
            self.segments.append(("\n", self.stack.copy()))

    def handle_endtag(self, tag):
        name = None
        if tag in ("b", "strong"):
            name = "bold"
        elif tag in ("i", "em"):
            name = "italic"
        elif tag == "span":
            # remove last color tag if present
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i] in _COLOR_HEX:
                    name = self.stack[i]
                    break
        if name:
            # eliminar la última ocurrencia de 'name' (pop correspondiente)
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i] == name:
                    self.stack.pop(i)
                    break

    def handle_data(self, data):
        if data:
            self.segments.append((data, self.stack.copy()))

def html_to_buffer(html_string, text_buffer, tag_map):
    """
    html_string: string con HTML
    text_buffer: Gtk.TextBuffer (debe tener creados los TextTag correspondientes)
    tag_map: dict name->Gtk.TextTag
    """
    parser = HTMLToSegmentsParser()
    parser.feed(html_string)

    # Coalesce segmentos contiguos con las mismas tags para eficiencia
    segs = []
    for text, tags in parser.segments:
        if segs and segs[-1][1] == tags:
            segs[-1] = (segs[-1][0] + text, tags)
        else:
            segs.append((text, tags))

    # Inserta todo el texto y aplica tags por rangos
    full_text = "".join(t for t, _ in segs)
    text_buffer.set_text(full_text, -1)

    offset = 0
    for text, tags in segs:
        if not text:
            continue
        length = len(text)
        start_iter = text_buffer.get_iter_at_offset(offset)
        end_iter = text_buffer.get_iter_at_offset(offset + length)
        for tag_name in tags:
            tag_obj = tag_map.get(tag_name)
            if tag_obj:
                text_buffer.apply_tag(tag_obj, start_iter, end_iter)
        offset += length





