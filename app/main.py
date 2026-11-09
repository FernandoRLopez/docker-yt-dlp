from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL
from pydantic import BaseModel
import os
import unicodedata

app = FastAPI(title="YouTube Audio Downloader", version="2.0.0")

# Download Directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Configuración API Key (lee de la variable de entorno, con fallback a tu clave de pruebas)
API_KEY = os.getenv("API_KEY", "mi-clave-de-pruebas")

def verificar_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verifica si la API Key proporcionada en la cabecera X-API-Key es válida."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida")
    return x_api_key

def limpiar_url(url: str) -> str:
    """Limpia la URL de YouTube para evitar errores de descarga."""
    if "&list=" in url:
        url = url.split("&list=")[0]
    if "index=" in url:
        url = url.split("&index=")[0]
    return url

def limpiar_titulo_youtube(url: str) -> str:
    """Extrae los metadatos, quita acentos, emojis, limita la longitud y deja un nombre limpio."""
    ydl_opts_info = {'noplaylist': True}
    
    with YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'cancion')
        video_id = info.get('id', 'unknown')
        
        # 1. Quitar acentos
        nfkd_form = unicodedata.normalize('NFKD', title)
        title_sin_acentos = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        
        # 2. Dejar solo caracteres seguros
        safe_title = "".join(c for c in title_sin_acentos if c.isalnum() or c in " -_").strip()
        
        # 3. Limitar longitud
        safe_title = safe_title[:50].strip()
        
        if not safe_title:
            safe_title = f"audiotrack-{video_id}"
            
        return safe_title

class AudioRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"status": "API funcionando correctamente"}

@app.post("/download/audio")
def download_audio(data: AudioRequest, _ = Depends(verificar_api_key)):
    clean_url = limpiar_url(data.url)
    
    # 1. Obtenemos el título limpio
    safe_title = limpiar_titulo_youtube(clean_url)
        
    # 2. Definimos la plantilla correctamente con .%(ext)s
    output_template = os.path.join(DOWNLOAD_DIR, f"{safe_title}.%(ext)s")
    expected_file = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': output_template,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])

    if not os.path.exists(expected_file):
        raise HTTPException(status_code=500, detail="Error: El archivo MP3 no se generó correctamente.")

    return FileResponse(expected_file, media_type="audio/mpeg", filename=f"{safe_title}.mp3")