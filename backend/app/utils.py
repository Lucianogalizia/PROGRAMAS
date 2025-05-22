# backend/app/utils.py

from io import BytesIO
import pandas as pd

def parse_datasheet(content: bytes) -> pd.DataFrame:
    """
    Lee el contenido binario de un archivo Excel y devuelve un pandas.DataFrame
    que representa el datasheet de entrada, validando que contenga las columnas
    mínimas necesarias.
    """
    # 1) Cargar el contenido en un buffer de memoria
    buffer = BytesIO(content)
    
    # 2) Leer la primera hoja del Excel con openpyxl
    df = pd.read_excel(buffer, engine="openpyxl")
    
    # 3) Validar que existan las columnas obligatorias
    required = ["POZO", "BATERÍA", "EQUIPO"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas obligatorias en el datasheet: {', '.join(missing)}")
    
    # 4) Retornar el DataFrame crudo para procesar en el pipeline
    return df
