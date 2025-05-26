# pulling-app/backend/app/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import traceback
import sys

app = FastAPI(title="Generador de Programas de Pulling")

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    # 1) Validar extensión
    if not file.filename.lower().endswith((".xls", ".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=400,
            detail="Formato inválido: se requiere un archivo Excel (.xls/.xlsx/.xlsm)."
        )

    content = await file.read()

    # 2) Abrir como ExcelFile y verificar que exista la hoja "Data Sheet"
    try:
        xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    except Exception:
        print("ERROR al abrir el Excel:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=400, detail="No pude abrir el Excel.")

    if "Data Sheet" not in xls.sheet_names:
        print("ERROR hoja faltante 'Data Sheet':", file=sys.stderr)
        raise HTTPException(
            status_code=400,
            detail="No encontré la pestaña 'Data Sheet' en el Excel."
        )

    # 3) Parsear solo la hoja "Data Sheet" sin cabeceras
    try:
        df0 = xls.parse("Data Sheet", header=None)
    except Exception:
        print("ERROR al parsear Data Sheet:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=400,
            detail="Error al parsear hoja 'Data Sheet'."
        )
    df = df0.copy()

    # 4) Helper para trocear tablas
    def slice_table(r0, r1, c0, c1, cols):
        try:
            t = df.iloc[r0:r1, c0:c1].copy()
            t.columns = cols
            return t.dropna(subset=[cols[0]])
        except Exception:
            print(f"ERROR extrayendo tabla filas[{r0}:{r1}] cols[{c0}:{c1}]:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise

    # 5) Extracción de las 4 tablas
    tubing_act = slice_table(
        r0=31, r1=54, c0=3,  c1=8,
        cols=["ELEMENTO","DIÁMETRO","PROFUNDIDAD","CANTIDAD","COMENTARIO"]
    )
    tubing_fin = slice_table(
        r0=31, r1=54, c0=10, c1=17,
        cols=[
            "ELEMENTO","CONDICIÓN","DIÁMETRO","PROFUNDIDAD",
            "CANTIDAD","COMENTARIO","LONGITUD ELEMENTO"
        ]
    )
    varillas_act = slice_table(
        r0=55, r1=78, c0=3,  c1=8,
        cols=["ELEMENTO","DIÁMETRO","PROFUNDIDAD","CANTIDAD","COMENTARIO"]
    )
    varillas_fin = slice_table(
        r0=55, r1=78, c0=10, c1=19,
        cols=[
            "ELEMENTO","CONDICIÓN","DIÁMETRO","PROFUNDIDAD",
            "ACERO V/B","CUPLA SH/FS","ACERO CUPLA","CANTIDAD","COMENTARIO"
        ]
    )

    # 6) Lectura de metadatos en celdas fijas (col D=idx3, E=idx4)
    meta_pos = {
        "POZO":               (2, 4),   # D3→E3
        "BATERIA":            (4, 4),   # D5→E5
        "EQUIPO":             (6, 4),   # D7→E7
        "NETA_ASOCIADA":      (8, 4),   # D9→E9
        "DEFINICION":         (10,4),   # D11→E11
        "MANIOBRAS_MOTIVO":   (12,4),   # D13→E13
        "PRIORIDAD_PROGRAMA": (14,4),   # D15→E15
        "ANTECEDENTE_1":      (17,4),   # D18→E18
        "ANTECEDENTE_2":      (18,4),
        "ANTECEDENTE_3":      (19,4),
        "ANTECEDENTE_4":      (20,4),
        "REQ_ESP_1":          (22,4),   # D23→E23
        "REQ_ESP_2":          (23,4),
        "REQ_ESP_3":          (24,4),
        "REQ_ESP_4":          (25,4),
    }
    meta = {}
    for key, (r, c) in meta_pos.items():
        try:
            meta[key] = df0.iat[r, c]
        except IndexError:
            meta[key] = None

    # 7) Armar resultado y devolver
    resultado = {
        "metadatos":       meta,
        "tubing_actual":   tubing_act.to_dict(orient="records"),
        "tubing_final":    tubing_fin.to_dict(orient="records"),
        "varillas_actual": varillas_act.to_dict(orient="records"),
        "varillas_final":  varillas_fin.to_dict(orient="records"),
    }
    return JSONResponse(content=resultado)




    



