import os
from fastapi import FastAPI, HTTPException, Header, Depends
from app.schemas import AudioRequest, AudioResponse, PlaylistResponse, VideoRequest, VideoResponse
from app.services import descargar_audio_youtube, descargar_playlist_youtube, descargar_video_youtube
from dotenv import load_dotenv


app = FastAPI(
    title="YouTube Audio Downloader API",
    version="3.2.0",
    description="API limpia y eficiente para integraciones con n8n y Navidrome."
)

load_dotenv()
API_KEY = os.getenv("API_KEY", "mi-clave-de-pruebas")

def verificar_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Valida la cabecera de seguridad X-API-Key.

    Esta dependencia comprueba que la solicitud incluye una clave válida
    antes de permitir el acceso a los endpoints protegidos. Si la cabecera
    falta o no coincide con la configuración del servicio, la petición se
    rechaza con un error 401.

    Args:
        x_api_key (str): Valor recibido en la cabecera X-API-Key.

    Returns:
        str: La clave verificada si es correcta.

    Raises:
        HTTPException: Si la clave no es válida o la cabecera no se incluye.
    """

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado: API Key inválida o faltante")
    return x_api_key

@app.get("/")
def read_root():
    """Endpoint raíz para comprobar el estado de la API.

    Este endpoint actúa como health check para validar que la aplicación
    sigue ejecutándose correctamente y que puede atender peticiones.

    Returns:
        dict: Mensaje simple con el estado operativo de la API.
    """
    return {"status": "API funcionando correctamente"}

@app.post("/download/audio", response_model=AudioResponse)
def endpoint_download_audio(data: AudioRequest, _ = Depends(verificar_api_key)):
    """Descarga el audio de un vídeo de YouTube y lo convierte a MP3.

    El flujo real del servicio consiste en limpiar la URL, extraer la
    información del vídeo con yt-dlp, sanitizar el título para usarlo como
    nombre de archivo, descargar el audio y convertirlo a formato MP3 con
    FFmpeg. Si la operación falla, la API responde con un error 500.

    Args:
        data (AudioRequest): Payload con la URL del vídeo a procesar.
        _ (str): Clave de API validada por la dependencia de seguridad.

    Returns:
        AudioResponse: Resultado de la operación con el estado, metadatos del
        vídeo y la ruta del archivo MP3 generado.

    Raises:
        HTTPException: Si ocurre un problema durante la extracción o la
        conversión del archivo.
    """
    try:
        resultado = descargar_audio_youtube(data.url)
        return {
            "success": True,
            "message": "Audio descargado correctamente",
            **resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download/playlist", response_model=PlaylistResponse)
def endpoint_download_playlist(data: AudioRequest, _ = Depends(verificar_api_key)):
    try:
        resultado = descargar_playlist_youtube(data.url)
        return {
            "success": True,
            **resultado
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la playlist: {str(e)}")


@app.post("/download/video", response_model=VideoResponse)
def endpoint_download_video(data: VideoRequest, _ = Depends(verificar_api_key)):
    try:
        resultado = descargar_video_youtube(data.url, data.quality)
        return {
            "success": True,
            "message": f"Vídeo descargado correctamente en {data.quality}p",
            **resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))