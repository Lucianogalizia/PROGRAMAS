from pandas import DataFrame
import pandas as pd

def bajada_varillas(df: DataFrame) -> list:
    """
    Módulo BAJADA DE VARILLAS:
    – Se activa si en INSTALACIÓN FINAL VARILLAS hay 'BAJA' en COMENTARIO.
    – Secuencia:
       1) ACONDICIONAMIENTO PARA BAJAR VARILLAS
       2) BAJA VARILLAS
       3) BAJA VARILLAS EN DOBLE o EN SIMPLE (solo uno)
       4) PRUEBA DE HERMETICIDAD
    """

    program = []

    # --- Extraer tabla final de varillas ---
    # Columnas esperadas
    cols = [c for c in [
        "ELEMENTO", "CONDICIÓN", "DIÁMETRO NOMINAL (in)",
        "PROFUNDIDAD", "ACERO V/B", "CUPLA SH/FS", "ACERO CUPLA",
        "CANTIDAD", "COMENTARIO"
    ] if c in df.columns]
    section = df[cols].copy()

    # Activación
    if not section["COMENTARIO"].str.contains("BAJA", case=False, na=False).any():
        return program

    # 1) ACONDICIONAMIENTO PARA BAJAR VARILLAS
    program.append({
        "manobra_normalizada": "ACONDICIONAMIENTO PARA  BAJAR VARILLAS",
        "punto_programa": 50,
        "descripcion": "Acondicionar boca de pozo, montar piso de trabajo + herramientas de v/b.",
        "activity_phase": "SP04",
        "activity_code": "SP16",
        "activity_subcode": "254",
        "tiempo": ""
    })

    # 2) BAJA VARILLAS
    program.append({
        "manobra_normalizada": "BAJA VARILLAS",
        "punto_programa": 51,
        "descripcion": "Limpiar todas las conexiones con detergente biodegradable.",
        "activity_phase": "SP04",
        "activity_code": "SP16",
        "activity_subcode": "255",
        "tiempo": ""
    })

    # --- L.1 Selección SIMPLE/DOBLE ---
    mode = None
    for _, row in section.iterrows():
        elem = str(row["ELEMENTO"]).upper()
        if "VARILLA DE BOMBEO" in elem:
            comm = str(row["COMENTARIO"] or "").upper()
            if "BAJA EN DOBLE" in comm:
                mode = "DOBLE"
            elif "BAJA EN SIMPLE" in comm:
                mode = "SIMPLE"
            break
    if not mode:
        # si no se encontró varilla de bombeo, no agregamos maniobra condicional
        mode = "SIMPLE"

    # Helper: construir diseño a bajar en orden inverso
    def build_design(sec: pd.DataFrame) -> str:
        parts = []
        for _, r in sec.iloc[::-1].iterrows():
            cant = int(r["CANTIDAD"]) if pd.notna(r["CANTIDAD"]) else None
            elem = str(r["ELEMENTO"]).strip()
            cond = r.get("CONDICIÓN")
            dia  = r.get("DIÁMETRO NOMINAL (in)")
            prof = r.get("PROFUNDIDAD")
            avb  = r.get("ACERO V/B")
            csfs = r.get("CUPLA SH/FS")
            ac   = r.get("ACERO CUPLA")
            comm = str(r.get("COMENTARIO") or "")

            if not cant:
                continue

            part = f"{cant} {elem}"
            if elem.upper() == "BOMBA CONVENCIONAL INSERTABLE BM" and pd.notna(prof):
                part += f" {int(prof)} mts"
            else:
                if pd.notna(cond):
                    part += f" {cond}"
                if pd.notna(dia):
                    part += f" {dia}"
                if pd.notna(avb):
                    part += f" {avb}"
                if pd.notna(csfs):
                    part += f" {csfs}"
                if pd.notna(ac):
                    part += f" {ac}"
            if comm:
                part += f" ({comm})"
            parts.append(part)
        return " + ".join(parts)

    design = build_design(section)

    # Condición: vincular on-off
    vincular = section["ELEMENTO"].str.contains(r"ON-OFF|BBA\.TBG\.PUMP", case=False, na=False).any()

    # 3) BAJA VARILLAS EN DOBLE o EN SIMPLE
    desc = (
        "Tomar datos de bomba y bajarla + sarta de v/b en doble limpiando todas las conexiones con detergente biodegradable. "
        "Realizar control de torque cada 15 varillas según grado de acero de varillas. "
        f"Diseño a bajar: {design}."
    )
    if vincular:
        desc += " vincular on-off."
    program.append({
        "manobra_normalizada": f"BAJA VARILLAS EN {mode}",
        "punto_programa": 54,
        "descripcion": desc,
        "activity_phase": "SP04",
        "activity_code": "SP16",
        "activity_subcode": "255",
        "tiempo": ""
    })

    # 4) PRUEBA DE HERMETICIDAD
    program.append({
        "manobra_normalizada": "PRUEBA DE HERMETICIDAD",
        "punto_programa": 49,
        "descripcion": (
            "Realizar PH final con 1000, 900 y 800 psi respectivamente. "
            "Junto a la prueba final, realizar prueba de funcionamiento de bomba. "
            "Registrar la misma en OpenWells. Si la prueba es deficiente informar a Supervisor de Pulling."
        ),
        "activity_phase": "SP03",
        "activity_code": "SP13",
        "activity_subcode": "205",
        "tiempo": ""
    })

    return program
