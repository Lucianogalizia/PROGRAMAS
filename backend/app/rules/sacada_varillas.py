# backend/app/rules/sacada_varillas.py

from pandas import DataFrame
import pandas as pd

def sacada_varillas(df: DataFrame) -> list:
    """
    Módulo SACADA DE VARILLAS (puntos programa 6–29):
    - Siempre:
      6. ACONDICIONA PARA SACAR VARILLAS
      7. SACA VARILLAS
      8. CIRCULA
      9. MANIOBRA HERRAMIENTA
    - H) Pesca de varillas (si MOTIVO contiene "Pesca de varilla"):
      10. SACA VARILLAS EN PESCA
      11. SACA VARILLAS EN PESCA EN DOBLE
    - J) Sacada normal (si no hay pesca):
      13. SACA VARILLAS EN DOBLE o SACA VARILLAS EN SIMPLE
    - Siempre al final de este bloque:
      29. DESARMA HERRAMIENTA
    """

    program = []
    row = df.iloc[0]
    motivo = str(row.get("MANIOBRAS (MOTIVO)") or "")

    # -- 6) ACONDICIONA PARA SACAR VARILLAS
    program.append({
        "manobra_normalizada": "ACONDICIONA PARA SACAR VARILLAS",
        "punto_programa": 6,
        "descripcion": (
            "Acondicionar boca de pozo, montar piso de trabajo + htas de v/b. "
            "Retirar vástago completo. Tomar peso de sarta, y registrar en OW."
        ),
        "activity_phase": "SP03",
        "activity_code": "SP24",
        "activity_subcode": "250",
        "tiempo": ""
    })

    # -- 7) SACA VARILLAS
    program.append({
        "manobra_normalizada": "SACA VARILLAS",
        "punto_programa": 7,
        "descripcion": "Maniobras varias durante la sacada de varillas.",
        "activity_phase": "SP03",
        "activity_code": "SP24",
        "activity_subcode": "251",
        "tiempo": ""
    })

    # -- 8) CIRCULA
    program.append({
        "manobra_normalizada": "CIRCULA",
        "punto_programa": 8,
        "descripcion": (
            "Circular pozo, 2.5 veces la capacidad de tubing por directa hasta retorno limpio "
            "para asegurar limpieza de los materiales extraídos. Si no se observa circulación "
            "informar si es por punta de instalación obstruida o porque el pozo admite."
        ),
        "activity_phase": "SP05",
        "activity_code": "SP20",
        "activity_subcode": "218",
        "tiempo": ""
    })

    # -- 9) MANIOBRA HERRAMIENTA
    program.append({
        "manobra_normalizada": "MANIOBRA HERRAMIENTA",
        "punto_programa": 9,
        "descripcion": "Maniobrar sarta y herramientas.",
        "activity_phase": "SP04",
        "activity_code": "SP18",
        "activity_subcode": "212",
        "tiempo": ""
    })

    # Construcción de "diseño a extraer" para todos los sub-bloques
    instal = df.loc[:, ["ELEMENTO", "DIÁMETRO (in)", "CANTIDAD", "COMENTARIO"]]
    diseño_parts = []
    bomba = None
    for _, v in instal.iterrows():
        elem = str(v["ELEMENTO"]).strip()
        cant = int(v["CANTIDAD"]) if pd.notna(v["CANTIDAD"]) else None
        dia = v["DIÁMETRO (in)"]
        com = str(v["COMENTARIO"] or "")
        # Separar bomba
        if elem.upper() == "BOMBA CONVENCIONAL INSERTABLE BM":
            bomba = f"{cant} {elem}"
            continue
        # Solo varillas/vástago/trozos
        if cant and dia and ("VARILLA" in elem.upper() or "VÁSTAGO" in elem.upper() or "TROZO" in elem.upper()):
            # Detectar conexión del comentario
            tipo = "SIMPLE" if "SACA EN SIMPLE" in com.upper() else "DOBLE"
            diseño_parts.append(f"{cant} {elem} ({tipo})")

    # Insertar bomba al final, si existe
    if bomba:
        diseño_parts.append(bomba)

    diseño = " + ".join(diseño_parts)

    # H) Pesca de varillas
    if "PESCA DE VARILLA" in motivo.upper():
        # 10) SACA VARILLAS EN PESCA
        program.append({
            "manobra_normalizada": "SACA VARILLAS EN PESCA",
            "punto_programa": 10,
            "descripcion": (
                f"Saca varillas en doble hasta punto de pesca, completando pozo. "
                f"Desarmar componentes que requieran reemplazo. Diseño a extraer: {diseño}. "
                "Asentar en OW observaciones significativas en cuanto a eventual presencia de "
                "corrosión, desgaste, incrustaciones o sobretorque. Registrar evidencia "
                "fotográfica del estado del material y punto de pesca. Asentar en OW grado de acero del material extraído."
            ),
            "activity_phase": "SP03",
            "activity_code": "SP24",
            "activity_subcode": "251",
            "tiempo": ""
        })
        # 11) SACA VARILLAS EN PESCA EN DOBLE (obligatorio tras pesca)
        # Determinar prefix según condiciones G.1.A
        instalaciones = df.filter(like="INSTALACIÓN ACTUAL")
        on_off = instalaciones.apply(lambda col: col.str.contains("ON-OFF", na=False)).any().any()
        pump = instalaciones.apply(lambda col: col.str.contains("BBA. TUB.PUMP", na=False)).any().any()
        if on_off:
            prefix = "Desvincular On&Off."
        elif pump:
            prefix = "Desclavar bomba."
        else:
            prefix = ""
        program.append({
            "manobra_normalizada": "SACA VARILLAS EN PESCA EN DOBLE",
            "punto_programa": 11,
            "descripcion": (
                f"Pescar. {prefix} Sacar varillas pescadas en doble, desarmando conexión par, "
                "completando pozo. Desarmar componentes que requieran reemplazo."
            ),
            "activity_phase": "SP03",
            "activity_code": "SP24",
            "activity_subcode": "251",
            "tiempo": ""
        })

    else:
        # J) Sacada normal (no pesca): elegir SIMPLE o DOBLE según primera ocurrencia
        # Condición general: debe haber bomba en varillas y NO on_off/pump
        has_bomba = any(df["ELEMENTO"].str.upper() == "BOMBA CONVENCIONAL INSERTABLE BM")
        instalaciones = df.filter(like="INSTALACIÓN ACTUAL")
        has_onoff = instalaciones.apply(lambda col: col.str.contains("ON-OFF", na=False)).any().any()
        has_pump = instalaciones.apply(lambda col: col.str.contains("BBA. TUB.PUMP", na=False)).any().any()

        if has_bomba and not (has_onoff or has_pump):
            # Buscar primera varilla de bombeo con SIMPLE o DOBLE
            primera = None
            for _, v in instal.iterrows():
                com = str(v["COMENTARIO"] or "").upper()
                if "VARILLA DE BOMBEO" in str(v["ELEMENTO"]).upper():
                    if "SACA EN DOBLE" in com:
                        primera = "DOBLE"
                        break
                    if "SACA EN SIMPLE" in com:
                        primera = "SIMPLE"
                        break

            if primera:
                desc = (
                    f"Desclavar bomba. Desplazar por directa para sacar sarta limpia. "
                    f"Sacar sarta en tiro {primera}, desarmando, completando pozo. Desarmar componentes "
                    f"que requieran reemplazo. Diseño a extraer: {diseño}. "
                    "Asentar en OW observaciones significativas en cuanto a eventual presencia de "
                    "corrosión, desgaste, incrustaciones o sobretorque. Registrar evidencia "
                    "fotográfica del estado del material. Asentar en OW grado de acero del material extraído."
                )
                program.append({
                    "manobra_normalizada": f"SACA VARILLAS EN {primera}",
                    "punto_programa": 13,
                    "descripcion": desc,
                    "activity_phase": "SP03",
                    "activity_code": "SP24",
                    "activity_subcode": "251",
                    "tiempo": ""
                })

    # -- 29) DESARMA HERRAMIENTA
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
