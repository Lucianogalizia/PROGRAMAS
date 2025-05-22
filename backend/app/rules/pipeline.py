# backend/app/rules/pipeline.py
# backend/app/rules/pipeline.py

from pandas import DataFrame
import pandas as pd

from .inicio import inicio
from .sacada_varillas import sacada_varillas
from .sacada_tubing import sacada_tubing
from .bajada_tubing import bajada_tubing
from .bajada_varillas import bajada_varillas
from .finalizacion import finalizacion

def activar_sacada_varillas(df: DataFrame) -> bool:
    """
    Devuelve True si:
      – DEFINICIÓN o MANIOBRAS (MOTIVO) contiene 'BM'
    Y – En INSTALACIÓN ACTUAL VARILLAS aparece un ELEMENTO con VARILLA, VÁSTAGO o TROZO VARILLA
      cuya fila tenga COMENTARIO con 'SACA'
    """
    row = df.iloc[0]
    defin  = str(row.get("DEFINICIÓN") or row.get("DEFINICION") or "").upper()
    motivo = str(row.get("MANIOBRAS (MOTIVO)") or "").upper()
    # 1) chequeo BM en definición o motivo
    if "BM" not in defin and "BM" not in motivo:
        return False

    # 2) filtrar filas de varillas
    mask_elem = df["ELEMENTO"].str.contains(r"VARILLA|VÁSTAGO|TROZO VARILLA", case=False, na=False)
    mask_com  = df["COMENTARIO"].str.contains(r"SACA", case=False, na=False)
    return (mask_elem & mask_com).any()

def build_program(df: DataFrame) -> list:
    """
    Orquesta los módulos de armado de programa de pulling:
    1. Inicio obligatorio
    2. Módulos condicionales
    3. Finalización obligatoria
    """
    program = []

    # 1) Módulo de inicio (Equipo en transporte, Montaje equipo, etc.)
    program += inicio(df)

    # 2) Módulos condicionales según contenido del datasheet

    # — SACADA DE VARILLAS
    if activar_sacada_varillas(df):
        program += sacada_varillas(df)

    # — SACADA DE TUBING (si aparece "SACA" en INSTALACIÓN ACTUAL TUBING)
    if df.filter(like="INSTALACIÓN ACTUAL TUBING") \
         .apply(lambda col: col.str.contains("SACA", na=False)).any().any():
        program += sacada_tubing(df)

    # — BAJADA DE TUBING (si aparece "BAJA" en INSTALACIÓN FINAL TUBING)
    if df.filter(like="INSTALACIÓN FINAL TUBING") \
         .apply(lambda col: col.str.contains("BAJA", na=False)).any().any():
        program += bajada_tubing(df)

    # — BAJADA DE VARILLAS (si aparece "BAJA" en INSTALACIÓN FINAL VARILLAS)
    if df.filter(like="INSTALACIÓN FINAL VARILLAS") \
         .apply(lambda col: col.str.contains("BAJA", na=False)).any().any():
        program += bajada_varillas(df)

    # 3) Módulo de finalización (Varios, Arma BDP, Desmonta equipo)
    program += finalizacion(df)

    return program


