# 🎵 YouTube Audio Downloader API (FastAPI + yt-dlp + Docker)

API backend desarrollada con **FastAPI** y **yt-dlp** para descargar audio de YouTube en formato MP3 de forma individual y limpia, containerizada con **Docker** y lista para integrarse con **n8n** en un entorno autoalojado (NanoPi / Servidor Linux).

---

## 🚀 Características Implementadas

- **Limpieza de URLs (`limpiar_url`):** Elimina automáticamente parámetros de listas de reproducción (`&list=`, `&index=`, etc.) para asegurar que siempre se procese y descargue una pista individual.
- **Procesamiento y Sanitización de Metadatos (`limpiar_titulo_youtube`):**
  - Extrae el título real del vídeo.
  - Normaliza Unicode y elimina acentos/diacríticos.
  - Filtra emojis y caracteres especiales (permite solo letras, números, espacios, guiones y guiones bajos).
  - Limita la longitud del título a un máximo de 50 caracteres para evitar errores en sistemas de archivos Linux.
  - **Fallback de seguridad:** Si el título queda vacío tras la limpieza, genera un nombre trazable tipo `audiotrack-{id}`.
- **Conversión a MP3 de alta calidad:** Integración con **FFmpeg** a nivel de sistema para extraer el mejor audio disponible (`bestaudio/best`).
- **Seguridad mediante API Key (`X-API-Key`):** Endpoint protegido mediante cabecera personalizada (`X-API-Key`), configurable mediante variables de entorno.
- **Gestión Correcta de Permisos en Docker (`uid/gid 1000`):** El contenedor ejecuta el proceso bajo el usuario no-root `1000:1000`, garantizando que los archivos `.mp3` generados en el volumen mapeado tengan los permisos de lectura/escritura del usuario host.

---

## 📁 Estructura del Proyecto

```text
docker-yt-dlp/
├── app/
│   ├── main.py
│   └── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🐳 Despliegue

```bash
sudo docker compose up --build -d
```
