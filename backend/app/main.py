from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from .utils import parse_datasheet
from .rules.pipeline import build_program

app = FastAPI(title="Generador de Programas de Pulling")

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    # Validar extensión
    if not file.filename.lower().endswith((".xls", ".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Formato inválido: se requiere un archivo Excel.")
    content = await file.read()

    # Parsear el datasheet a DataFrame
    try:
        df = parse_datasheet(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el datasheet: {e}")

    # Generar programa de maniobras
    try:
        program = build_program(df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el programa: {e}")

    return JSONResponse(content={"program": program})
