import os
from dataclasses import dataclass

@dataclass
class Config:
    """Configuración de la aplicación"""

    #Conf. DB
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "ElPorteno")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "placeres88")

    # Necesarios para la visualización y API:

    HEXAGRAMA = {
        "h1": "111111", "h2": "000000", "h3": "010001", "h4": "100010", "h5": "010111",
        "h6": "111010", "h7": "000010", "h8": "010000", "h9": "110111", "h10": "111011",
        "h11": "000111", "h12": "111000", "h13": "111101", "h14": "101111", "h15": "000100",
        "h16": "001000", "h17": "011001", "h18": "100110", "h19": "000011", "h20": "110000",
        "h21": "101001", "h22": "100101", "h23": "100000", "h24": "000001", "h25": "111001",
        "h26": "100111", "h27": "100001", "h28": "011110", "h29": "010010", "h30": "101101",
        "h31": "011100", "h32": "001110", "h33": "111100", "h34": "001111", "h35": "101000",
        "h36": "000101", "h37": "110101", "h38": "101011", "h39": "010100", "h40": "001010",
        "h41": "100011", "h42": "110001", "h43": "011111", "h44": "111110", "h45": "011000",
        "h46": "000110", "h47": "011010", "h48": "010110", "h49": "011101", "h50": "101110",
        "h51": "001001", "h52": "100100", "h53": "110100", "h54": "001011", "h55": "001101",
        "h56": "101100", "h57": "110110", "h58": "011011", "h59": "110010", "h60": "010011",
        "h61": "110011", "h62": "001100", "h63": "010101", "h64": "101010", "h0": ""
    }

    PATTERN_BUSCAR_ID = r"\A[0-9]+$"

    #Rutas
    RESUMEN_ICON_PATH = "ui/icons/block_note.png"
    TEXT_EDITOR_ICON_PATH = "ui/icons/text_editor.png"

    #Conf. Aplicación
    APP_NAME: str = "El Porteño - Index"
    VERSION: str = "3.0.0"

config = Config()
