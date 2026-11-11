FROM python:3.10-slim

# Instalar FFmpeg a nivel de sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar los requerimientos desde la raíz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la carpeta app al contenedor
COPY app/ ./app/

EXPOSE 8000

# IMPORTANTE: Como main.py está dentro de la carpeta app, se llama app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]