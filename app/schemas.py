from pydantic import BaseModel, Field
from typing import List, Literal

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
    playlist_title: str
    total_processed: int
    items: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "playlist_title": "Mi Playlist Favorita",
                "total_processed": 2,
                "items": [
                    {
                        "success": True,
                        "original_title": "Cancion 1",
                        "sanitized_title": "Cancion 1",
                        "video_id": "abc123xyz",
                        "file_name": "Cancion 1.mp3",
                        "file_path": "downloads/Cancion 1.mp3"
                    },
                    {
                        "success": False,
                        "video_id": "def456uvw",
                        "error": "Video unavailable"
                    }
                ]
            }
        }

class VideoRequest(BaseModel):
    url: str = Field(..., description="URL de YouTube del vídeo")
    quality: Literal["720", "1080"] = Field("720", description="Calidad máxima del vídeo: 720 o 1080")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.youtube.com/watch?v=BkCIoZJPQmg",
                "quality": "720"
            }
        }

class VideoResponse(BaseModel):
    success: bool
    message: str
    original_title: str
    sanitized_title: str
    video_id: str
    quality: str
    file_name: str
    file_path: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Vídeo descargado correctamente",
                "original_title": "Video de Ejemplo",
                "sanitized_title": "Video de Ejemplo",
                "video_id": "BkCIoZJPQmg",
                "quality": "720",
                "file_name": "Video de Ejemplo.mp4",
                "file_path": "downloads/Video de Ejemplo.mp4"
            }
        }