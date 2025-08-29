import asyncio
import websockets
import http.server
import socketserver
import threading
import requests

# Configuración
WORKER_URL = "wss://host.streamgramm.workers.dev/tunnel"
SECRET = "ec2cb31c0cd22b340d5f7874027afa2828a2c9f639192dfaaced05df5628bb11"
LOCAL_PORT = 8080

# Servidor HTTP local (ejemplo)
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Servidor Local Expuesto via Cloudflare Worker</h1>")
        else:
            self.send_error(404)

def start_local_server():
    with socketserver.TCPServer(("127.0.0.1", LOCAL_PORT), Handler) as httpd:
        print(f"Servidor local en http://127.0.0.1:{LOCAL_PORT}")
        httpd.serve_forever()

# Cliente túnel
async def tunnel_client():
    async with websockets.connect(WORKER_URL, extra_headers={"X-Auth-Secret": SECRET}) as ws:
        print("Conectado al Cloudflare Worker Tunnel")
        while True:
            req = await ws.recv()  # Recibimos petición del Worker
            print("Petición recibida desde Worker:", req)
            
            # Redirigimos a servidor local
            try:
                r = requests.get(f"http://127.0.0.1:{LOCAL_PORT}")
                await ws.send(r.text)
            except Exception as e:
                await ws.send(f"Error: {e}")

# Main
if __name__ == "__main__":
    threading.Thread(target=start_local_server, daemon=True).start()
    asyncio.get_event_loop().run_until_complete(tunnel_client())
