"""
Phone-as-Webcam — Desktop server (Windows).

Sirve una pagina web al celular (HTTPS), recibe frames de la camara del
celular por WebSocket y los publica como CAMARA VIRTUAL del PC usando el
driver de OBS Virtual Camera (pyvirtualcam).

Requisitos:
  - Python 3.9+
  - pip install -r requirements.txt
  - OBS Studio instalado (provee el driver de camara virtual de Windows).
    No hace falta tener OBS abierto, solo instalado una vez.

Uso:
  python server.py
Luego en el celular abre la URL que muestra la ventana (acepta el aviso
de certificado), pulsa "Iniciar" y permite el acceso a la camara.
"""

import asyncio
import datetime
import ipaddress
import socket
import ssl
import threading
from pathlib import Path

import cv2
import numpy as np
from aiohttp import web, WSMsgType

# ---- Config de la camara virtual ----
WIDTH = 1280
HEIGHT = 720
FPS = 30
PORT = 8443

BASE_DIR = Path(__file__).resolve().parent
CERT_FILE = BASE_DIR / "cert.pem"
KEY_FILE = BASE_DIR / "key.pem"
INDEX_FILE = BASE_DIR / "index.html"

# Frame compartido entre el hilo del WebSocket (productor) y el hilo
# de la camara virtual (consumidor).
_latest_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
_frame_lock = threading.Lock()
_running = True
_clients = 0
_status_cb = None  # callback que la GUI registra para mostrar estado


def _set_status(text: str):
    if _status_cb:
        _status_cb(text)


def get_local_ip() -> str:
    """IP LAN del PC (la que ve el celular)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No envia nada; solo fuerza al SO a elegir la interfaz de salida.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def ensure_cert(ip: str):
    """Genera un certificado autofirmado con la IP actual en el SAN."""
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ip)])

    san = [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
    try:
        san.append(x509.IPAddress(ipaddress.ip_address(ip)))
    except ValueError:
        pass

    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow() - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
        .sign(key, hashes.SHA256())
    )

    KEY_FILE.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


# ---- Handlers HTTP / WebSocket ----
async def handle_index(request):
    return web.FileResponse(INDEX_FILE)


async def handle_ws(request):
    global _clients
    ws = web.WebSocketResponse(max_msg_size=16 * 1024 * 1024)
    await ws.prepare(request)
    _clients += 1
    _set_status(f"Celular conectado ({_clients})")

    try:
        async for msg in ws:
            if msg.type == WSMsgType.BINARY:
                # Decodifica JPEG -> BGR y lo guarda como frame actual.
                arr = np.frombuffer(msg.data, dtype=np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                if frame is None:
                    continue
                if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
                    frame = cv2.resize(frame, (WIDTH, HEIGHT))
                with _frame_lock:
                    np.copyto(_latest_frame, frame)
            elif msg.type == WSMsgType.ERROR:
                break
    finally:
        _clients -= 1
        _set_status("Esperando celular..." if _clients == 0 else f"Celular conectado ({_clients})")
    return ws


def build_app():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/ws", handle_ws)
    return app


def run_http_server(ip: str):
    """Corre aiohttp en su propio hilo con su event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)

    runner = web.AppRunner(build_app())
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, "0.0.0.0", PORT, ssl_context=ctx)
    loop.run_until_complete(site.start())
    loop.run_forever()


def run_virtual_camera():
    """Hilo consumidor: empuja el frame mas reciente a la camara virtual."""
    import pyvirtualcam

    placeholder = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    cv2.putText(placeholder, "Esperando celular...", (340, HEIGHT // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)

    try:
        with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
            _set_status(f"Camara virtual activa: {cam.device}")
            while _running:
                with _frame_lock:
                    if _latest_frame.any():
                        frame = _latest_frame.copy()
                    else:
                        frame = placeholder
                # pyvirtualcam espera RGB.
                cam.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cam.sleep_until_next_frame()
    except Exception as e:
        _set_status(f"ERROR camara virtual: {e}")


def start(status_cb=None):
    """Arranca todo. Devuelve la URL para el celular."""
    global _status_cb
    _status_cb = status_cb

    ip = get_local_ip()
    ensure_cert(ip)

    threading.Thread(target=run_http_server, args=(ip,), daemon=True).start()
    threading.Thread(target=run_virtual_camera, daemon=True).start()

    return f"https://{ip}:{PORT}/"


if __name__ == "__main__":
    # Modo consola (sin GUI), por si se quiere correr asi.
    url = start(status_cb=lambda s: print("[estado]", s))
    print("Abre esta URL en el celular:", url)
    print("Ctrl+C para salir.")
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        _running = False
