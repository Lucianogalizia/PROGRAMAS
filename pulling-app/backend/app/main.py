# pulling-app/backend/app/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io

from .rules.pipeline import build_program

app = FastAPI(title="Generador de Programas de Pulling")

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    # Validar extensión
    if not file.filename.lower().endswith((".xls", ".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Formato inválido: se requiere un archivo Excel.")

    # Leer todo el contenido en memoria
    content = await file.read()

    # Intentar abrir el Excel y localizar la hoja "Data Sheet"
    try:
        xls = pd.ExcelFile(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo Excel: {e}")

    if "Data Sheet" not in xls.sheet_names:
        raise HTTPException(status_code=400, detail="No encontré la pestaña 'Data Sheet' en el Excel.")

    try:
        df = xls.parse("Data Sheet")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear la hoja 'Data Sheet': {e}")

    # Generar programa de maniobras
    try:
        program = build_program(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el programa: {e}")

    return JSONResponse(content={"program": program})

