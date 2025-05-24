# pulling-app/backend/app/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .utils import parse_datasheet
from .rules.pipeline import build_program

app = FastAPI(title="Generador de Programas de Pulling")

# ---- Añadimos CORS aquí ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # o pon el dominio de tu frontend
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xls", ".xlsx", ".xlsm")):
        raise HTTPException(400, "Formato inválido: se requiere un archivo Excel.")

    content = await file.read()

    # parsear
    try:
        df = parse_datasheet(content)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # generar programa
    try:
        program = build_program(df)
    except Exception as e:
        raise HTTPException(500, f"Error al generar el programa: {e}")

    return JSONResponse({"program": program})


