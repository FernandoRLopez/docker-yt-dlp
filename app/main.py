from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL
import os
import unicodedata

app = FastAPI()

# Download Directory
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def limpiar_url (url: str) -> str:
    """Limpia la URL de YouTube para evitar errores de descarga."""
    if "&list=" in url:
        url = url.split("&list=")[0]  # Elimina la parte de la lista de reproducción
    if "index=" in url:
        url = url.split("&index=")[0]  # Elimina la parte del índice
    return url

def limpiar_titulo_youtube(url: str) -> str:
    """Extrae los metadatos, quita acentos, emojis, limita la longitud y deja un nombre limpio."""
    ydl_opts_info = {'noplaylist': True}
    
    with YoutubeDL(ydl_opts_info) as ydl:
        # Extraemos la información del vídeo sin descargarlo todavía
        info = ydl.extract_info(url, download=False)
        title = info.get('title', 'cancion')
        video_id = info.get('id', 'unknown')
        
        # 1. Quitar acentos convirtiendo caracteres Unicode (ej: á -> a)
        nfkd_form = unicodedata.normalize('NFKD', title)
        title_sin_acentos = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        
        # 2. Dejar solo letras, números, espacios, guiones y guiones bajos (elimina emojis y símbolos raros)
        safe_title = "".join(c for c in title_sin_acentos if c.isalnum() or c in " -_").strip()
        
        # 3. Limitar la longitud máxima (ej: máximo 50 caracteres) para evitar nombres kilométricos y errores en Linux
        max_length = 50
        safe_title = safe_title[:max_length].strip()
        
        # Si por lo que sea se queda vacío tras la limpieza
        if not safe_title:
            safe_title = f"audiotrack-{video_id}"
            
        return safe_title


@app.get("/")
def read_root():
    return {"status": "API funcionando correctamente"}




@app.post("/download/audio")
def download_audio(url: str):
    # 1. Obtenemos el título limpio usando nuestra función auxiliar
    safe_title = limpiar_titulo_youtube(url)
        
    # 2. Definimos la ruta final donde se guardará el MP3
    output_template = os.path.join(DOWNLOAD_DIR, safe_title)
    expected_file = f"{output_template}.mp3"


    # Opciones básicas de yt-dlp: guarda directamente como cancion.mp3 en la carpeta
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': output_template,
        'noplaylist': True,
    }

    # Ejecución directa sin control de errores ni carpetas temporales
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


    # Devolvemos el archivo directamente
    return FileResponse(expected_file, media_type="audio/mpeg", filename=f"{safe_title}.mp3")

