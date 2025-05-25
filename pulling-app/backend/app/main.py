# pulling-app/backend/app/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io

app = FastAPI(title="Generador de Programas de Pulling")

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    # 1) Validar extensión
    if not file.filename.lower().endswith((".xls", ".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Formato inválido: se requiere un archivo Excel.")
    content = await file.read()

    # 2) Cargar el Excel en un DataFrame sin cabeceras
    try:
        df0 = pd.read_excel(io.BytesIO(content),
                            sheet_name="Data Sheet",
                            header=None,
                            engine="openpyxl")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No pude abrir el Excel: {e}")
    df = df0.copy()

    # 3) Extraer tablas por posición fija
    def slice_table(row_start, row_end, col_start, col_end, cols):
        t = df.iloc[row_start:row_end, col_start:col_end].copy()
        t.columns = cols
        return t.dropna(subset=[cols[0]])

    tubing_act = slice_table(
        row_start=31, row_end=54, col_start=3, col_end=8,
        cols=["ELEMENTO","DIÁMETRO","PROFUNDIDAD","CANTIDAD","COMENTARIO"]
    )
    tubing_fin = slice_table(
        row_start=31, row_end=54, col_start=10, col_end=17,
        cols=["ELEMENTO","CONDICIÓN","DIÁMETRO","PROFUNDIDAD",
              "CANTIDAD","COMENTARIO","LONGITUD ELEMENTO"]
    )
    varillas_act = slice_table(
        row_start=55, row_end=78, col_start=3, col_end=8,
        cols=["ELEMENTO","DIÁMETRO","PROFUNDIDAD","CANTIDAD","COMENTARIO"]
    )
    varillas_fin = slice_table(
        row_start=55, row_end=78, col_start=10, col_end=19,
        cols=["ELEMENTO","CONDICIÓN","DIÁMETRO","PROFUNDIDAD",
              "ACERO V/B","CUPLA SH/FS","ACERO CUPLA","CANTIDAD","COMENTARIO"]
    )

    # 4) Leer metadatos de celdas fijas (D-fila, E-fila)
    #    0-based index sobre df0: columna D→idx 3, E→idx 4
    meta_pos = {
        "POZO":                   (2, 4),   # D3→E3
        "BATERIA":                (4, 4),   # D5→E5
        "EQUIPO":                 (6, 4),   # D7→E7
        "NETA_ASOCIADA":          (8, 4),   # D9→E9
        "DEFINICION":             (10,4),   # D11→E11
        "MANIOBRAS_MOTIVO":       (12,4),   # D13→E13
        "PRIORIDAD_PROGRAMA":     (14,4),   # D15→E15
        "ANTECEDENTE_1":          (17,4),   # D18→E18
        "ANTECEDENTE_2":          (18,4),
        "ANTECEDENTE_3":          (19,4),
        "ANTECEDENTE_4":          (20,4),
        "REQ_ESP_1":              (22,4),   # D23→E23
        "REQ_ESP_2":              (23,4),
        "REQ_ESP_3":              (24,4),
        "REQ_ESP_4":              (25,4),
    }
    meta = {}
    for key, (r, c) in meta_pos.items():
        try:
            meta[key] = df0.iat[r, c]
        except IndexError:
            meta[key] = None

    # 5) Empaquetar todo en la respuesta
    resultado = {
        "metadatos": meta,
        "tubing_actual": tubing_act.to_dict(orient="records"),
        "tubing_final":  tubing_fin.to_dict(orient="records"),
        "varillas_actual": varillas_act.to_dict(orient="records"),
        "varillas_final":  varillas_fin.to_dict(orient="records"),
    }

    return JSONResponse(content=resultado)



