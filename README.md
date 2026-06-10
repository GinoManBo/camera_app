# Camara desde el celular (Windows)

Usa tu celular como webcam del PC. El celular captura video y lo envia por
WiFi al PC, que lo publica como **camara virtual** usable en Zoom, Teams,
Discord, Meet, OBS, etc.

```
[Celular: navegador] --WiFi/WebSocket--> [PC: server.py] --> Camara virtual --> Zoom/Teams/...
```

## Que necesitas (una sola vez)

1. **Python 3.9+** en Windows: https://www.python.org/downloads/
   - En el instalador marca **"Add Python to PATH"**.
2. **OBS Studio** (gratis): https://obsproject.com/
   - Solo hay que instalarlo; provee el driver "OBS Virtual Camera" de Windows.
   - No hace falta abrir OBS.
3. PC y celular en la **misma red WiFi**.

## Como usar

1. En el PC, doble clic en **`Iniciar.bat`**.
   - La primera vez instala las dependencias (tarda un poco).
   - Se abre una ventana con un **codigo QR** y una **URL** `https://...:8443/`.
2. En el celular, **escanea el QR** (o escribe la URL en el navegador).
3. El navegador avisa que el certificado no es seguro (es normal, es
   autofirmado). Pulsa **Avanzado -> Continuar / Aceptar el riesgo**.
4. En la pagina pulsa **Iniciar** y **permite** el acceso a la camara.
   - Boton "Girar camara" cambia entre frontal/trasera.
5. En tu app de video (Zoom/Teams/etc) elige la camara **"OBS Virtual Camera"**.

## Problemas comunes

- **No aparece "OBS Virtual Camera"**: instala OBS Studio y reinicia el PC.
- **El celular no carga la pagina**: revisa que estan en la misma WiFi y que
  el Firewall de Windows permite Python (acepta el aviso la primera vez).
- **El navegador no deja usar la camara**: tiene que ser por `https://`
  (la URL del QR ya lo es) y hay que aceptar el certificado.
- **iPhone/Safari**: usa Safari; acepta el certificado y los permisos de camara.
- **Imagen con retraso/lag**: baja `QUALITY` en `index.html` (ej. 0.5) o `FPS`.

## Ajustes

- Resolucion / FPS de la camara virtual: `WIDTH`, `HEIGHT`, `FPS` en `server.py`.
- Calidad/fps de envio del celular: `QUALITY`, `FPS` en `index.html`.
- Puerto: `PORT` en `server.py` (por defecto 8443).

## Archivos

- `app.py` — ventana de escritorio (QR + estado). Arranca todo.
- `server.py` — servidor HTTPS + WebSocket + camara virtual.
- `index.html` — pagina que se abre en el celular.
- `Iniciar.bat` — lanzador para Windows.
- `requirements.txt` — dependencias de Python.
