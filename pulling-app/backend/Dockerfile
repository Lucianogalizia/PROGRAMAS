# Usa una imagen oficial de Python
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la app
COPY app ./app

# Expone el puerto por defecto de Cloud Run
EXPOSE 8080

# Arranca Uvicorn apuntando a tu FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
