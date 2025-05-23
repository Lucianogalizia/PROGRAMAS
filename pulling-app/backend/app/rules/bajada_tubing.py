from pandas import DataFrame
import pandas as pd
import math

def bajada_tubing(df: DataFrame) -> list:
    """
    Módulo BAJADA DE TUBING:
    – Se activa si en INSTALACIÓN FINAL TUBING hay 'BAJA' en COMENTARIO.
    – Secuencia:
       1) ACONDICIONAMIENTO PARA BAJAR CAÑOS
       2) BAJA TUBING
       3) Condicional: BAJA TUBING DESAGOTANDO
       4) Sino: BAJA TUBING EN DOBLE o EN SIMPLE
       5) ACONDICIONA PARA PH
       6) PRUEBA DE HERMETICIDAD (con variante si hay SHEAR OUT)
    """

    program = []

    # --- Extraer sección final de tubing ---
    # Filtrar columnas de instalación final tubing
    final_cols = df.filter(like="INSTALACIÓN FINAL TUBING").columns
    section = df[final_cols].copy()
    # Renombrar a nombres uniformes
    col_map = {}
    for c in section.columns:
        uc = c.upper()
        if "ELEMENTO" in uc:       col_map[c] = "elemento"
        elif "CONDICIÓN" in uc:    col_map[c] = "condicion"
        elif "DIÁMETRO" in uc:     col_map[c] = "diametro"
        elif "PROFUNDIDAD" in uc:  col_map[c] = "profundidad"
        elif "CANTIDAD" in uc:     col_map[c] = "cantidad"
        elif "COMENTARIO" in uc:   col_map[c] = "comentario"
    section.rename(columns=col_map, inplace=True)

    # Activación del módulo
    if not section["comentario"].str.contains("BAJA", na=False).any():
        return program

    # --- Maniobras obligatorias ---
    program.append({
        "manobra_normalizada": "ACONDICIONAMIENTO PARA BAJAR CAÑOS",
        "punto_programa": 36,
        "descripcion": "Completar pozo con ASDF y retirar BOP. Empaquetar pozo.",
        "activity_phase": "SP04",
        "activity_code": "SP16",
        "activity_subcode": "256",
        "tiempo": ""
    })
    program.append({
        "manobra_normalizada": "BAJA TUBING",
        "punto_programa": 37,
        "descripcion": "Tareas generales durante la bajada de tubing.",
        "activity_phase": "SP04",
        "activity_code": "SP16",
        "activity_subcode": "257",
        "tiempo": ""
    })

    # Prefijo por ancla en cualquier maniobra de bajada
    anchor_present = section["elemento"].str.upper().eq("ANCLA").any()
    anchor_prefix = "Librar ANCLA. " if anchor_present else ""

    # Helper: construir diseño a bajar en orden inverso
    def build_design(df_sec: pd.DataFrame) -> str:
        parts = []
        for _, row in df_sec.iloc[::-1].iterrows():
            elem = str(row["elemento"]).strip()
            cant = int(row["cantidad"]) if pd.notna(row["cantidad"]) else None
            dia = row.get("diametro")
            cond = row.get("condicion")
            prof = row.get("profundidad")
            comm = str(row.get("comentario") or "")
            if cant:
                part = f"{cant} {elem}"
                if pd.notna(dia):
                    part += f" {dia}"
                if elem.upper() == "ANCLA" and pd.notna(prof):
                    part += f" EN {int(prof)}"
                if pd.notna(cond) and elem.upper() != "ANCLA":
                    part += f" {cond}"
                # incluir comentario entre paréntesis (solo para 'BAJA EN ...')
                if "BAJA" in comm.upper():
                    part += f" ({comm})"
                parts.append(part)
        return " + ".join(parts)

    # --- BAJA TUBING DESAGOTANDO (M.1) ---
    req_esp = str(df.iloc[0].get("REQUERIMIENTO ESPECIAL") or "").upper()
    if "SACAR/BAJAR TUBING DESAGOTANDO" in req_esp:
        design = build_design(section)

        # Determinar profundidad de ancla
        anchor_row = section[section["elemento"].str.upper() == "ANCLA"]
        if not anchor_row.empty and pd.notna(anchor_row.iloc[0]["profundidad"]):
            anchor_depth = float(anchor_row.iloc[0]["profundidad"])
        else:
            # fallback zapato
            zap = section[section["elemento"].str.upper() == "ZAPATO"]
            if not zap.empty and pd.notna(zap.iloc[0]["profundidad"]):
                anchor_depth = float(zap.iloc[0]["profundidad"])
            else:
                # fallback bomba
                bomb = section[section["elemento"].str.upper().str.contains("BOMBA", na=False)]
                if not bomb.empty and pd.notna(bomb.iloc[0]["profundidad"]):
                    anchor_depth = float(bomb.iloc[0]["profundidad"])
                else:
                    raise ValueError(
                        "No se detectó profundidad de ANCLA ni de ZAPATO ni de BOMBA; "
                        "por favor indicar manualmente profundidad de ancla."
                    )

        # Cálculo de tensión y estiramiento
        COEF_POISSON = 0.3
        MODULO_YOUNG = 30_000_000
        COEF_EXPANSION = 0.0000069
        GRADIENTE_FLUIDO = 0.5
        CONV_PM = 3.28084
        NIV_EL_EST = 656.17
        TEMP_SUP = 30
        TEMP_MED = 15

        nivel_dyn_m = anchor_depth - 200
        nivel_dyn_ft = nivel_dyn_m * CONV_PM

        tubing_rows = section[section["elemento"].str.upper() == "TUBING"]
        if not tubing_rows.empty:
            diam = float(tubing_rows.iloc[0]["diametro"])
            area = math.pi * (diam ** 2) / 4
        else:
            area = 0

        F1 = area * nivel_dyn_ft * GRADIENTE_FLUIDO * (
            (COEF_POISSON * nivel_dyn_ft / anchor_depth) + (1 - 2 * COEF_POISSON)
        )
        F2 = MODULO_YOUNG * COEF_EXPANSION * ((TEMP_SUP - TEMP_MED) / 2) * area * 0  # pendiente definir sección paredes
        F3 = 0  # pendiente cálculo exacto
        tension = F1 + F2 - F3
        estiramiento = 0.22 * (nivel_dyn_ft / 1000) * (tension / 1000)

        desc = (
            f"{anchor_prefix}"
            "Profundizar columna de TBG calibrando, midiendo, limpiando, engrasando y torqueando las conexiones. "
            f"Bajar desagotando con copa de pistoneo. Diseño a bajar: {design}. "
            "Asentar en OW observaciones significativas. "
            f"Fijar ancla con {tension:.0f} lbs y {estiramiento:.2f} in de estiramiento."
        )
        program.append({
            "manobra_normalizada": "BAJA TUBING DESAGOTANDO",
            "punto_programa": 38,
            "descripcion": desc,
            "activity_phase": "SP04",
            "activity_code": "SP16",
            "activity_subcode": "257",
            "tiempo": ""
        })

    else:
        # --- M.2 Selección DOBLE / SIMPLE ---
        design = build_design(section)
        mode = None
        for comm in section["comentario"].str.upper():
            if "BAJA EN DOBLE" in comm:
                mode = "DOBLE"
                break
            if "BAJA EN SIMPLE" in comm:
                mode = "SIMPLE"
                break
        if mode:
            desc = (
                f"{anchor_prefix}"
                "Profundizar columna de TBG calibrando, midiendo, limpiando, engrasando y torqueando las conexiones. "
                f"Bajar columna de tubing en tiro {mode.lower()}. Diseño a bajar: {design}. "
                "Asentar en OW observaciones significativas."
            )
            # agregar tensión de ancla si corresponde
            if anchor_present:
                # reusar tension/estiramiento previo o recalcular brevemente
                desc += f" Fijar ancla con {tension:.0f} lbs y {estiramiento:.2f} in de estiramiento."
            program.append({
                "manobra_normalizada": f"BAJA TUBING EN {mode}",
                "punto_programa": 38,
                "descripcion": desc,
                "activity_phase": "SP04",
                "activity_code": "SP16",
                "activity_subcode": "257",
                "tiempo": ""
            })

    # --- M.4 Finalización del módulo de bajada ---
    # ACONDICIONA PARA PH
    program.append({
        "manobra_normalizada": "ACONDICIONA PARA PH",
        "punto_programa": 47,
        "descripcion": "Acondicionar superficie para realizar prueba hidráulica.",
        "activity_phase": "SP03",
        "activity_code": "SP13",
        "activity_subcode": "259",
        "tiempo": ""
    })
    # PRUEBA DE HERMETICIDAD (variante si hay SHEAR OUT)
    shear_present = section["elemento"].str.upper().eq("SHEAR OUT").any()
    if shear_present:
        descripcion_ph = (
            "Realizar PH inicial, final 1000 psi. Expulsar SO de 4 pines con 2023 psi. "
            "Junto a la prueba final, realizar prueba de funcionamiento de bomba. "
            "Registrar la misma en OpenWells. Si la prueba es deficiente, informar a Supervisor de Pulling."
        )
    else:
        descripcion_ph = (
            "Realizar PH inicial, intermedia y final con 1000, 900 y 800 psi respectivamente. "
            "Junto a la prueba final, realizar prueba de funcionamiento de bomba. "
            "Registrar la misma en OpenWells. Si la prueba es deficiente, informar a Supervisor de Pulling."
        )
    program.append({
        "manobra_normalizada": "PRUEBA DE HERMETICIDAD",
        "punto_programa": 49,
        "descripcion": descripcion_ph,
        "activity_phase": "SP03",
        "activity_code": "SP13",
        "activity_subcode": "205",
        "tiempo": ""
    })

    return program
