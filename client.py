import asyncio
import websockets
import requests
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# ---------------- Configuración ----------------
WORKER_URL = "wss://host.streamgramm.workers.dev/tunnel"
SECRET = "ec2cb31c0cd22b340d5f7874027afa2828a2c9f639192dfaaced05df5628bb11"
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 8080
# ----------------------------------------------

# Servidor local de ejemplo (puedes reemplazar con tu bot)
class LocalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Ruta: {parsed_path.path}, Query: {query}".encode())

def start_local_server():
    server = HTTPServer((LOCAL_HOST, LOCAL_PORT), LocalHandler)
    print(f"Servidor local corriendo en http://{LOCAL_HOST}:{LOCAL_PORT}")
    server.serve_forever()

# Cliente WebSocket hacia Worker
async def tunnel_client():
    while True:
        try:
            async with websockets.connect(
                WORKER_URL, extra_headers={"X-Auth-Secret": SECRET}
            ) as ws:
                print("Conectado al Cloudflare Worker (túnel estilo Ngrok)")

                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    path = data.get("path", "/")

                    # Forward a servidor local
                    try:
                        resp = requests.get(f"http://{LOCAL_HOST}:{LOCAL_PORT}{path}")
                        response_data = {"status": resp.status_code, "content": resp.text}
                    except Exception as e:
                        response_data = {"error": str(e)}

                    await ws.send(json.dumps(response_data))

        except Exception as e:
            print("Error de conexión, reconectando en 5s...", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=start_local_server, daemon=True).start()
    asyncio.get_event_loop().run_until_complete(tunnel_client())
