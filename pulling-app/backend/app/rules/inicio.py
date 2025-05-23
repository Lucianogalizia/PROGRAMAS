# pulling-app/backend/app/rules/inicio.py

import pandas as pd
from pandas import DataFrame

def inicio(df: DataFrame) -> list:
    """
    Módulo de inicio: siempre retorna las maniobras iniciales
    EQUIPO EN TRANSPORTE, MONTAJE EQUIPO, CONTROL DE POZO,
    DESARMA BDP y ARMA HERRAMIENTA.
    """
    row = df.iloc[0]

    # Campos básicos
    pozo = row["POZO"]
    definicion = row.get("DEFINICIÓN") or row.get("DEFINICION", "")
    motivo = row.get("MANIOBRAS (MOTIVO)") or row.get("MANIOBRAS", "")

    # Antecedentes
    anteced_cols = [c for c in df.columns if c.upper().startswith("ANTECEDENTES")]
    antecedentes = [str(row[c]) for c in anteced_cols if pd.notna(row[c])]

    # Requerimientos
    req_cols = [c for c in df.columns if c.upper().startswith("REQUERIMIENTO ESPECIAL")]
    requerimientos = [str(row[c]) for c in req_cols if pd.notna(row[c])]

    # Descripción dinámica de EQUIPO EN TRANSPORTE
    desc_et = f"Transportar a {pozo}."
    if antecedentes:
        desc_et += f" Tener en cuenta los antecedentes del pozo: {', '.join(antecedentes)}."
    desc_et += f" La definición actual del pozo es: {definicion}."
    desc_et += f" La maniobra a realizar es {motivo}."
    if requerimientos:
        desc_et += f" Considerar los siguientes requerimientos: {', '.join(requerimientos)}."

    return [
        {
            "manobra_normalizada": "EQUIPO EN TRANSPORTE",
            "punto_programa": 1,
            "descripcion": desc_et,
            "activity_phase": "S01",
            "activity_code": "SP10",
            "activity_subcode": "200",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "MONTAJE EQUIPO",
            "punto_programa": 2,
            "descripcion": "Verificar presiones por directa y por entrecaño. Desarmar puente de producción. Montar equipo según procedimiento.",
            "activity_phase": "S01",
            "activity_code": "SP10",
            "activity_subcode": "201",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "CONTROL DE POZO",
            "punto_programa": 3,
            "descripcion": "Controlar presiones por directa y entrecaño, desplazamiento y emanaciones de gas de pozo.",
            "activity_phase": "SP05",
            "activity_code": "SP20",
            "activity_subcode": "220",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "DESARMA BDP",
            "punto_programa": 4,
            "descripcion": "Desarmar BDP.",
            "activity_phase": "SP03",
            "activity_code": "SP34",
            "activity_subcode": "210",
            "tiempo": ""
        },
        {
            "manobra_normalizada": "ARMA HERRAMIENTA",
            "punto_programa": 5,
            "descripcion": "Armar herramienta.",
            "activity_phase": "SP04",
            "activity_code": "SP15",
            "activity_subcode": "209",
            "tiempo": ""
        },
    ]

