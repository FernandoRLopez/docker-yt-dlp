from pydantic import BaseModel, Field
from typing import List

class AudioRequest(BaseModel):
    """Modelo de entrada para solicitar la descarga de audio desde YouTube.

    Recibe la URL de un vídeo individual o de una playlist que será
    procesada por la API para convertirlo a formato MP3.
    """
    url: str = Field(..., description="URL de YouTube del vídeo o playlist")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=BkCIoZJPQmg"
            }
        }

class AudioResponse(BaseModel):
    """Resultado de una descarga individual de audio.

    Este modelo representa la respuesta final tras extraer el audio de un
    vídeo de YouTube y convertirlo a MP3. Incluye tanto la información
    del archivo generado como los metadatos básicos del recurso original.
    """
    success: bool
    message: str
    original_title: str
    sanitized_title: str
    video_id: str
    file_name: str
    file_path: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Audio descargado correctamente",
                "original_title": "Cancion de Ejemplo",
                "sanitized_title": "Cancion de Ejemplo",
                "video_id": "abc123xyz",
                "file_name": "Cancion de Ejemplo.mp3",
                "file_path": "downloads/Cancion de Ejemplo.mp3"
            }
        }

class PlaylistResponse(BaseModel):
    """Resultado de la descarga de una playlist completa.

    Devuelve el estado global de la operación y una lista con el resultado
    de cada elemento procesado dentro de la playlist. Cada elemento incluye
    la información asociada a la descarga individual de cada vídeo.
    """
    success: bool
    total_processed: int
    items: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_processed": 1,
                "items": [
                    {
                        "success": True,
                        "original_title": "Cancion de Ejemplo",
                        "sanitized_title": "Cancion de Ejemplo",
                        "video_id": "abc123xyz",
                        "file_name": "Cancion de Ejemplo.mp3",
                        "file_path": "downloads/Cancion de Ejemplo.mp3"
                    }
                ]
            }
        }