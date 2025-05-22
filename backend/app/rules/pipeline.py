# backend/app/rules/pipeline.py

from pandas import DataFrame
from .inicio import inicio
from .sacada_varillas import sacada_varillas
from .sacada_tubing import sacada_tubing
from .bajada_tubing import bajada_tubing
from .bajada_varillas import bajada_varillas
from .finalizacion import finalizacion

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
    # Sacada de varillas si en la instalación actual de varillas aparece "SACA"
    if df.filter(like="INSTALACIÓN ACTUAL VARILLAS").apply(lambda col: col.str.contains("SACA", na=False)).any().any():
        program += sacada_varillas(df)

    # Sacada de tubing si en la instalación actual de tubing aparece "SACA"
    if df.filter(like="INSTALACIÓN ACTUAL TUBING").apply(lambda col: col.str.contains("SACA", na=False)).any().any():
        program += sacada_tubing(df)

    # Bajada de tubing si en la instalación final de tubing aparece "BAJA"
    if df.filter(like="INSTALACIÓN FINAL TUBING").apply(lambda col: col.str.contains("BAJA", na=False)).any().any():
        program += bajada_tubing(df)

    # Bajada de varillas si en la instalación final de varillas aparece "BAJA"
    if df.filter(like="INSTALACIÓN FINAL VARILLAS").apply(lambda col: col.str.contains("BAJA", na=False)).any().any():
        program += bajada_varillas(df)

    # 3) Módulo de finalización (Varios, Arma BDP, Desmonta equipo)
    program += finalizacion(df)

    return program
