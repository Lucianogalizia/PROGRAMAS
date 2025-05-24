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

import logging
import traceback

logger = logging.getLogger("uvicorn.error")

@app.post("/process/")
async def process(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = parse_datasheet(content)
        program = build_program(df)
    except Exception as e:
        # Esto escribirá el stack completo en stderr
        logger.error("Error en /process/:\n%s", traceback.format_exc())
        # Y luego devolvemos el 500
        raise HTTPException(status_code=500, detail="Error interno. Revisa los logs.")
    return JSONResponse(content={"program": program})


