# backend/app/rules/sacada_tubing.py

import pandas as pd
from pandas import DataFrame

def sacada_tubing(df: DataFrame) -> list:
    """
    Módulo SACADA DE TUBING:
    – Se activa si hay 'SACA' en comentarios de INSTALACIÓN ACTUAL TUBING.
    – Secuencia general:
       1) ACONDICIONA PARA PH
       2) PRUEBA DE HERMETICIDAD
       3) ACONDICIONAMIENTO PARA SACAR CAÑOS
       4) SACA TUBING
       5) Condicional:
          • SACA TUBING DESAGOTANDO
          • SACA TUBING EN PESCA
          • SACA TUBING EN DOBLE / SIMPLE
       6) DESARMA HERRAMIENTA
    """

    # 0) Filtrar tubing a sacar
    mask = df["COMENTARIO"].str.contains("SACA", case=False, na=False)
    tubing_rows = df.loc[mask, ["ELEMENTO", "DIÁMETRO (in)", "CANTIDAD", "COMENTARIO"]]
    if tubing_rows.empty:
        return []

    program = []

    # Detectar ANCLA
    anchor_present = df["ELEMENTO"].str.contains("ANCLA", case=False, na=False).any()
    anchor_prefix = "Librar ANCLA. " if anchor_present else ""

    # 1) ACONDICIONA PARA PH
    program.append({
        "manobra_normalizada": "ACONDICIONA PARA PH",
        "punto_programa": 47,
        "descripcion": "Acondicionar superficie para realizar prueba hidráulica.",
        "activity_phase": "SP03",
        "activity_code": "SP13",
        "activity_subcode": "259",
        "tiempo": ""
    })

    # 2) PRUEBA DE HERMETICIDAD
    program.append({
        "manobra_normalizada": "PRUEBA DE HERMETICIDAD",
        "punto_programa": 49,
        "descripcion": (
            "Realizar PH con 1000, 900 y 800 psi respectivamente. "
            "Informar si la misma es positiva si es necesario mover columna de tubing."
        ),
        "activity_phase": "SP03",
        "activity_code": "SP13",
        "activity_subcode": "205",
        "tiempo": ""
    })

    # 3) ACONDICIONAMIENTO PARA SACAR CAÑOS
    program.append({
        "manobra_normalizada": "ACONDICIONAMIENTO PARA SACAR CAÑOS",
        "punto_programa": 15,
        "descripcion": (
            "Acondicionar boca de pozo, completar con ASDF, desempaquetar y montar conjunto BOP anular. "
            "Montar piso de trabajo."
        ),
        "activity_phase": "SP03",
        "activity_code": "SP24",
        "activity_subcode": "252",
        "tiempo": ""
    })

    # 4) SACA TUBING
    program.append({
        "manobra_normalizada": "SACA TUBING",
        "punto_programa": 16,
        "descripcion": "Tareas generales durante la sacada de tubing.",
        "activity_phase": "SP03",
        "activity_code": "SP24",
        "activity_subcode": "253",
        "tiempo": ""
    })

    # Construir diseño para cualquier rama
    def build_design(rows):
        parts = []
        for _, row in rows.iterrows():
            elem = str(row["ELEMENTO"]).strip()
            cant = int(row["CANTIDAD"]) if pd.notna(row["CANTIDAD"]) else None
            dia = row["DIÁMETRO (in)"]
            com = str(row["COMENTARIO"] or "")
            if cant:
                part = f"{cant} {elem}"
                if pd.notna(dia):
                    part += f" {dia}"
                # Para DESAGOTANDO: tipo conexión si "SACA" en comentario
                if "SACA" in com.upper():
                    tipo = "DOBLE" if "DOBLE" in com.upper() else "SIMPLE"
                    part += f" EN {tipo}"
                parts.append(part)
        return " + ".join(parts)

    # 5.a) SACA TUBING DESAGOTANDO
    req_esp = str(df.iloc[0].get("REQUERIMIENTO ESPECIAL") or "").upper()
    if "SACAR/BAJAR TUBING DESAGOTANDO" in req_esp:
        # usar todas las filas de tubing actual para el diseño
        all_rows = df.loc[:, ["ELEMENTO", "DIÁMETRO (in)", "CANTIDAD", "COMENTARIO"]]
        design = build_design(all_rows)
        program.append({
            "manobra_normalizada": "SACA TUBING DESAGOTANDO",
            "punto_programa": 17,
            "descripcion": (
                f"{anchor_prefix}"
                "Desplazar por directa para sacar sarta limpia. "
                "Sacar sarta de tubing desagotando con copa de pistoneo, buscando pérdida y completando pozo. "
                "En caso de identificar algún tubing en falla, informar profundidad. "
                "Desarmar componentes que requieran reemplazo. "
                f"Diseño a extraer: {design}. "
                "Asentar en OW observaciones significativas en cuanto a eventual presencia de corrosión, desgaste o sobretorque. "
                "Registrar evidencia fotográfica del estado del material. "
                "Asentar en OW grado de acero del material extraído. "
                "Solicitar envío de bomba a taller de inmediato para desarmar e inspeccionar. "
                "Indicar si evidencia falla visible. Asentar número de bomba y estado de cabezal y filtro."
            ),
            "activity_phase": "SP03",
            "activity_code": "SP24",
            "activity_subcode": "253",
            "tiempo": ""
        })
        # 6) DESARMA HERRAMIENTA
        program.append({
            "manobra_normalizada": "DESARMA HERRAMIENTA",
            "punto_programa": 29,
            "descripcion": "Desarmar herramienta.",
            "activity_phase": "SP03",
            "activity_code": "SP25",
            "activity_subcode": "229",
            "tiempo": ""
        })
        return program

    # 5.b) L.2: SACA TUBING EN SIMPLE o EN DOBLE
    # Construir diseño solo con filas de tubing a sacar
    design_simple = build_design(tubing_rows)

    # elegir primer tipo según aparición
    first_type = None
    for com in tubing_rows["COMENTARIO"].str.upper():
        if "DOBLE" in com:
            first_type = "DOBLE"
            break
        if "SIMPLE" in com:
            first_type = "SIMPLE"
            break
    first_type = first_type or "SIMPLE"

    program.append({
        "manobra_normalizada": f"SACA TUBING EN {first_type}",
        "punto_programa": 20,
        "descripcion": (
            f"{anchor_prefix}"
            "Desplazar por directa para sacar sarta limpia. "
            f"Sacar sarta en tiro {first_type}, buscando pérdida y completando pozo. "
            "Desarmar componentes que requieran reemplazo. "
            f"Diseño a extraer: {design_simple}. "
            "Asentar en OW observaciones significativas en cuanto a eventual presencia de corrosión, desgaste o sobretorque. "
            "Registrar evidencia fotográfica del estado del material. "
            "Asentar en OW grado de acero del material extraído."
        ),
        "activity_phase": "SP03",
        "activity_code": "SP24",
        "activity_subcode": "253",
        "tiempo": ""
    })

    # 6) DESARMA HERRAMIENTA
    program.append({
        "manobra_normalizada": "DESARMA HERRAMIENTA",
        "punto_programa": 29,
        "descripcion": "Desarmar herramienta.",
        "activity_phase": "SP03",
        "activity_code": "SP25",
        "activity_subcode": "229",
        "tiempo": ""
    })

    return program
