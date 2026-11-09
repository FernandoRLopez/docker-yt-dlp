## 🎵 YouTube to MP3 FastAPI API

API backend minimalista desarrollada con **FastAPI** y **yt-dlp** para descargar audio de YouTube en formato MP3 de forma individual y limpia, diseñada para integrarse posteriormente con n8n y ejecutarse en un entorno Docker con almacenamiento mapeado a una NanoPi.

### 🚀 Características implementadas
- **Limpieza de URLs (`limpiar_url`):** Elimina automáticamente parámetros de listas de reproducción (`&list=`, `&index=`, etc.) para asegurar que siempre se procese una pista individual.
- **Procesamiento de Metadatos (`limpiar_titulo_youtube`):** 
  - Extrae el título real del vídeo.
  - Normaliza y elimina acentos (conversión Unicode).
  - Filtra emojis y caracteres especiales (solo permite letras, números, espacios, guiones y guiones bajos).
  - Limita la longitud del nombre a un máximo de 50 caracteres para evitar errores en sistemas Linux/Docker.
  - **Fallback de seguridad:** Si el título queda vacío tras la limpieza, asigna automáticamente un nombre seguro tipo `audiotrack-{id}` para facilitar la trazabilidad.
- **Conversión a MP3:** Integración con FFmpeg para extraer la mejor calidad de audio disponible (`bestaudio/best`).
- **Directorio Fijo de Descargas:** Los archivos se almacenan de forma organizada en la carpeta local `downloads/`, lista para ser mapeada mediante volúmenes en Docker.

### 📌 Próximos pasos pendientes
- [ ] Implementar endpoint para descarga de vídeo (MP4).
- [ ] Añadir capa de autenticación por API Key (para llamadas seguras desde n8n).
- [ ] Empaquetado final en `Dockerfile` y `docker-compose.yml` para despliegue en NanoPi.