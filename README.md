


# 🎵 YouTube Downloader & Media API (FastAPI + yt-dlp + FFmpeg + Docker)

API backend desarrollada con FastAPI y `yt-dlp` para la descarga automatizada y limpia de audio, listas de reproducción y vídeos desde YouTube, containerizada con Docker y diseñada para integrarse perfectamente en entornos autoalojados (como n8n y Navidrome).

---

## Características Implementadas

- **Arquitectura Modular de 3 Archivos (`app/`):** Estructura limpia y mantenible basada en `main.py` (rutas), `services.py` (lógica de `yt-dlp`) y `schemas.py` (validación con Pydantic).
- **Estructura de Directorios Organizada:**
  - `downloads/songs/`: Audio individual convertido a MP3 con **portada embebida obligatoria** (ideal para Navidrome).
  - `downloads/playlists/`: Listas de reproducción organizadas en subcarpetas con el título de la propia playlist.
  - `downloads/videos/`: Vídeos descargados con calidad seleccionable (`720` o `1080`) y contenedor MP4 optimizado.
- **Limpieza y Sanitización de Metadatos:**
  - Normalización de títulos (eliminación de acentos, emojis y caracteres especiales incompatibles con Linux).
  - Control de longitud máxima de nombres y sistemas de fallback por ID de vídeo.
- **Seguridad mediante API Key (`X-API-Key`):** Endpoints protegidos mediante cabecera personalizada validada por dependencias de FastAPI.
- **Gestión de Permisos en Docker (uid/gid 1000):** Ejecución bajo usuario no-root para asegurar permisos correctos en los volúmenes del host.

---

## 📁 Estructura del Proyecto

```
docker-yt-dlp/
├── app/
│   ├── main.py
│   ├── services.py
│   └── schemas.py
├── downloads/
│   ├── songs/
│   ├── playlists/
│   └── videos/
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```


## 🔌 Endpoints Disponibles

1. **`POST /download/audio`**
    
    - **Descripción:** Descarga un audio individual en formato MP3 con la miniatura incrustada automáticamente en la carpeta `downloads/songs/`.
        
    - **Body JSON:** `{"url": "[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)..."}`
        
2. **`POST /download/playlist`**
    
    - **Descripción:** Procesa una playlist, creando una subcarpeta específica en `downloads/playlists/` y descargando cada pista con su carátula integrada.
        
    - **Body JSON:** `{"url": "[https://www.youtube.com/playlist?list=](https://www.youtube.com/playlist?list=)..."}`
        
3. **`POST /download/video`**
    
    - **Descripción:** Descarga un vídeo individual eligiendo la calidad máxima en la carpeta `downloads/videos/`.
        
    - **Body JSON:** `{"url": "[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)...", "quality": "720"}` _(o "1080")_
        

## 🐳 Despliegue con Docker

Bash

```
sudo docker compose up --build -d
```