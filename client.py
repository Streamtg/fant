import asyncio
import websockets
import requests
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configuración
WORKER_URL = "wss://host.streamgramm.workers.dev/tunnel"
SECRET = "ec2cb31c0cd22b340d5f7874027afa2828a2c9f639192dfaaced05df5628bb11"
LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 8080

# Servidor HTTP local ejemplo
class LocalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/video"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Contenido de video simulado desde servidor local")
        elif self.path.startswith("/download"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Descarga simulada desde servidor local")
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ruta no encontrada")

def start_local_server():
    server = HTTPServer((LOCAL_HOST, LOCAL_PORT), LocalHandler)
    print(f"Servidor local corriendo en http://{LOCAL_HOST}:{LOCAL_PORT}")
    server.serve_forever()

# Cliente WebSocket hacia Worker
async def tunnel_client():
    async with websockets.connect(WORKER_URL, extra_headers={"X-Auth-Secret": SECRET}) as ws:
        print("Conectado al Cloudflare Worker Tunnel")
        while True:
            try:
                message = await ws.recv()
                data = json.loads(message)
                path = data.get("path", "/")
                
                # Forward a servidor local
                resp = requests.get(f"http://{LOCAL_HOST}:{LOCAL_PORT}{path}")
                
                # Enviar respuesta al Worker
                response_data = {
                    "status": resp.status_code,
                    "content": resp.text
                }
                await ws.send(json.dumps(response_data))
            except Exception as e:
                print("Error en el túnel:", e)

if __name__ == "__main__":
    threading.Thread(target=start_local_server, daemon=True).start()
    asyncio.get_event_loop().run_until_complete(tunnel_client())
