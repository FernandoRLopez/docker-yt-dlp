import os
import unicodedata
from yt_dlp import YoutubeDL

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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
        raise RuntimeError("El archivo MP3 no se generó correctamente en disco.")

    return {
        "success": True,
        "original_title": title,
        "sanitized_title": safe_title,
        "video_id": video_id,
        "file_name": f"{safe_title}.mp3",
        "file_path": expected_file
    }

def descargar_playlist_youtube(url: str) -> list:
    """Procesa una playlist de YouTube y descarga cada vídeo incluido.

    La función obtiene la lista de entradas de la playlist, genera la URL de
    cada vídeo y reutiliza la lógica de descarga individual para convertir
    todos los elementos a MP3. Si alguna canción falla durante el proceso,
    se registra el error sin interrumpir el resto de la iteración.

    Args:
        url (str): URL de la playlist de YouTube que se desea procesar.

    Returns:
        list: Lista de diccionarios con el resultado de cada elemento. Cada
        entrada incluye el estado, el identificador del vídeo y, cuando ocurre,
        el error asociado.
    """
    with YoutubeDL({'extract_flat': True, 'noplaylist': False}) as ydl:
        playlist_info = ydl.extract_info(url, download=False)
        entries = playlist_info.get('entries', [])

    resultados = []
    for entry in entries:
        video_id = entry.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            res = descargar_audio_youtube(video_url)
            resultados.append(res)
        except Exception as e:
            resultados.append({
                "success": False,
                "video_id": video_id,
                "error": str(e)
            })
            
    return resultados