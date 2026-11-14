import os
import unicodedata
from yt_dlp import YoutubeDL

#############################
# Global configuration
#############################

# Especific and base directories for downloads.

BASE_DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
SONGS_DIR = os.path.join(BASE_DOWNLOAD_DIR, "songs")
PLAYLISTS_DIR = os.path.join(BASE_DOWNLOAD_DIR, "playlists")
VIDEOS_DIR = os.path.join(BASE_DOWNLOAD_DIR, "videos")

# To create the directories if they don't exist, we use os.makedirs with exist_ok=True.
for directory in [SONGS_DIR, PLAYLISTS_DIR, VIDEOS_DIR]:
    os.makedirs(directory, exist_ok=True)








############################
# Helpers functions
############################

def limpiar_url(url: str) -> str:
    """Normaliza una URL de YouTube eliminando parámetros de seguimiento.

    Este helper elimina fragmentos como ``&list=`` y ``&index=`` que no
    forman parte del vídeo original y pueden interferir con la extracción
    de metadatos o la descarga.

    Args:
        url (str): URL completa del vídeo o de una referencia de YouTube.

    Returns:
        str: La URL limpia, reducida al enlace principal del recurso.
    """
    if "&list=" in url:
        url = url.split("&list=")[0]
    if "index=" in url:
        url = url.split("&index=")[0]
    return url

def sanitizar_texto(texto: str) -> str:
    """Genera un nombre de archivo seguro a partir de un título.

    Se eliminan acentos, caracteres diacríticos, emojis y símbolos no
    válidos para la mayoría de sistemas de archivos. También se limita la
    longitud final para evitar nombres excesivamente largos.

    Args:
        texto (str): Título original del vídeo o canción.

    Returns:
        str: Versión segura y limpia del texto, lista para usarse como nombre
        de archivo.
    """
    nfkd_form = unicodedata.normalize('NFKD', texto)
    sin_acentos = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    safe_title = "".join(c for c in sin_acentos if c.isalnum() or c in " -_").strip()
    return safe_title[:50].strip()

############################
# Audio Download Functions
############################

def descargar_audio_youtube(url: str) -> dict:
    """Descarga y convierte a MP3 un único vídeo de YouTube.

    La función limpia la URL, extrae los metadatos del recurso, genera un
    nombre seguro para el archivo, descarga el audio en la mejor calidad
    disponible y lo convierte a formato MP3 mediante FFmpeg. Si el archivo
    final no existe tras la conversión, lanza un error.

    Args:
        url (str): URL del vídeo de YouTube que se desea descargar.

    Returns:
        dict: Diccionario con el resultado de la operación, incluyendo el
        título original, el nombre sanitizado, el identificador del vídeo y
        la ruta del MP3 generado.

    Raises:
        RuntimeError: Si la conversión no produce el archivo MP3 esperado.
    """
    clean_url = limpiar_url(url)
    
    with YoutubeDL({'noplaylist': True}) as ydl:
        info = ydl.extract_info(clean_url, download=False)
        title = info.get('title', 'cancion')
        video_id = info.get('id', 'unknown')
        
    safe_title = sanitizar_texto(title)
    if not safe_title:
        safe_title = f"audiotrack-{video_id}"
        
    output_template = os.path.join(SONGS_DIR, f"{safe_title}.%(ext)s")
    expected_file = os.path.join(SONGS_DIR, f"{safe_title}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            },
            {
                'key': 'EmbedThumbnail' 
            }  
        ],
        'outtmpl': output_template,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])

    if not os.path.exists(expected_file):
        raise RuntimeError("El archivo MP3 no se generó correctamente en disco.")

    return {
        "success": True,
        "original_title": title,
        "sanitized_title": safe_title,
        "video_id": video_id,
        "file_name": f"{safe_title}.mp3",
        "file_path": expected_file
    }

#############################
# Playlist Download Function
#############################
def descargar_playlist_youtube(url: str) -> dict:
    """Extrae los elementos de una playlist y descarga cada pista dentro de su subcarpeta en 'playlists'."""
    ydl_opts_info = {
        'extract_flat': True,
        'noplaylist': False,
        'quiet': True
    }
    
    with YoutubeDL(ydl_opts_info) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        playlist_title = playlist_info.get('title', 'Playlist sin título')
        entries = playlist_info.get('entries', [])

    if not entries:
        raise ValueError("No se encontraron vídeos en la URL proporcionada o no es una playlist válida.")

    # Crear una subcarpeta específica para esta playlist dentro de downloads/playlists/
    safe_playlist_name = sanitizar_texto(playlist_title)
    playlist_folder = os.path.join(PLAYLISTS_DIR, safe_playlist_name)
    os.makedirs(playlist_folder, exist_ok=True)

    resultados = []
    for entry in entries:
        video_id = entry.get('id')
        if not video_id:
            continue
            
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            # Reutilizamos la lógica pero redirigiendo el destino a la carpeta de la playlist
            res = descargar_audio_personalizado(video_url, playlist_folder)
            resultados.append(res)
        except Exception as e:
            resultados.append({
                "success": False,
                "video_id": video_id,
                "error": str(e)
            })
            
    return {
        "playlist_title": playlist_title,
        "total_processed": len(resultados),
        "items": resultados
    }

def descargar_audio_personalizado(url: str, destino_dir: str) -> dict:
    """Función auxiliar para descargar un audio en un directorio específico (usada por playlists)."""
    clean_url = limpiar_url(url)
    with YoutubeDL({'noplaylist': True}) as ydl:
        info = ydl.extract_info(clean_url, download=False)
        title = info.get('title', 'cancion')
        video_id = info.get('id', 'unknown')
        
    safe_title = sanitizar_texto(title)
    if not safe_title:
        safe_title = f"audiotrack-{video_id}"
        
    output_template = os.path.join(destino_dir, f"{safe_title}.%(ext)s")
    expected_file = os.path.join(destino_dir, f"{safe_title}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            },
            {
                'key': 'EmbedThumbnail' 
            }
        ],
        'outtmpl': output_template,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])

    return {
        "success": True,
        "original_title": title,
        "sanitized_title": safe_title,
        "video_id": video_id,
        "file_name": f"{safe_title}.mp3",
        "file_path": expected_file
    }



###########################
# Video Download Function
###########################

def descargar_video_youtube(url: str, quality: str = "720") -> dict:
    """Procesa y descarga un único vídeo de YouTube a la calidad especificada (720 o 1080)."""
    clean_url = limpiar_url(url)
    
    with YoutubeDL({'noplaylist': True}) as ydl:
        info = ydl.extract_info(clean_url, download=False)
        title = info.get('title', 'video')
        video_id = info.get('id', 'unknown')
        
    safe_title = sanitizar_texto(title)
    if not safe_title:
        safe_title = f"videotrack-{video_id}"
        
    output_template = os.path.join(VIDEOS_DIR, f"{safe_title}.%(ext)s")
    expected_file = os.path.join(VIDEOS_DIR, f"{safe_title}.mp4")

    # Mapeo de calidad a formato de yt-dlp combinando mejor video (hasta X altura) y mejor audio
    if quality == "1080":
        format_selector = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    else:
        format_selector = "bestvideo[height<=720]+bestaudio/best[height<=720]"

    ydl_opts = {
        'format': format_selector,
        'merge_output_format': 'mp4', # Forzar contenedor MP4 final con FFmpeg
        'outtmpl': output_template,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])

    if not os.path.exists(expected_file):
        raise RuntimeError("El archivo de vídeo MP4 no se generó correctamente en disco.")

    return {
        "success": True,
        "original_title": title,
        "sanitized_title": safe_title,
        "video_id": video_id,
        "quality": quality,
        "file_name": f"{safe_title}.mp4",
        "file_path": expected_file
    }