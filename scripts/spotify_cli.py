#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import base64
import argparse

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"\'')
    except FileNotFoundError:
        pass

def get_env_var(name, required=False):
    val = os.environ.get(name)
    if required and not val:
        print(f"ERROR: Variable de entorno {name} no configurada en .env", file=sys.stderr)
        sys.exit(1)
    return val

class SpotifyClient:
    def __init__(self):
        self.client_id = get_env_var("SPOTIFY_CLIENT_ID", True)
        self.client_secret = get_env_var("SPOTIFY_CLIENT_SECRET", True)
        self.refresh_token = get_env_var("SPOTIFY_REFRESH_TOKEN", False)
        self.access_token = None

    def get_access_token(self):
        if self.access_token:
            return self.access_token
        if not self.refresh_token:
            print("ERROR: SPOTIFY_REFRESH_TOKEN no está configurado. Ejecuta el comando 'auth' primero.", file=sys.stderr)
            sys.exit(1)
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()
        
        data = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }).encode()
        
        req = urllib.request.Request(
            'https://accounts.spotify.com/api/token',
            data=data,
            headers={
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        try:
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read())
                self.access_token = res['access_token']
                return self.access_token
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            print(f"Error obteniendo token: {msg}", file=sys.stderr)
            sys.exit(1)

    def _api_request(self, method, endpoint, payload=None):
        token = self.get_access_token()
        url = f"https://api.spotify.com/v1{endpoint}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = None
        if payload is not None:
            data = json.dumps(payload).encode()
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return None
                body = resp.read()
                if not body:
                    return None
                return json.loads(body)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()
            print(f"Spotify API Error ({e.code}): {msg}", file=sys.stderr)
            sys.exit(1)

    def status(self):
        res = self._api_request('GET', '/me/player')
        if not res:
            print("No hay reproducción activa.")
            return
        item = res.get('item', {})
        state = "Playing" if res.get('is_playing') else "Paused"
        device = res.get('device', {}).get('name', 'Unknown')
        name = item.get('name', 'Unknown') if item else 'Unknown'
        artists = ", ".join([a['name'] for a in item.get('artists', [])]) if item and 'artists' in item else ''
        print(f"Status: {state}")
        print(f"Track: {name} - {artists}")
        print(f"Device: {device}")
        
        vol = res.get('device', {}).get('volume_percent')
        print(f"Volume: {vol}%" if vol is not None else "Volume: Unknown")

    def devices(self):
        res = self._api_request('GET', '/me/player/devices')
        devs = res.get('devices', [])
        if not devs:
            print("No se encontraron dispositivos activos.")
            return
        for d in devs:
            active = "*" if d['is_active'] else " "
            vol = d.get('volume_percent', 'N/A')
            print(f"[{active}] {d['name']} (ID: {d['id']}, Type: {d['type']}, Volume: {vol}%)")

    def play(self, device_id=None):
        endpoint = '/me/player/play'
        if device_id:
            import time
            for _ in range(3):
                res = self._api_request('GET', '/me/player/devices')
                devs = res.get('devices', [])
                if any(d['id'] == device_id and d['is_active'] for d in devs):
                    break
                time.sleep(2)
            else:
                print("Error: device no estabilizado todavía", file=sys.stderr)
                sys.exit(1)
            endpoint += f"?device_id={device_id}"
        self._api_request('PUT', endpoint)
        print(f"Reproducción iniciada{f' en {device_id}' if device_id else ''}.")

    def pause(self, device_id=None):
        endpoint = '/me/player/pause'
        if device_id:
            endpoint += f"?device_id={device_id}"
        self._api_request('PUT', endpoint)
        print(f"Reproducción pausada{f' en {device_id}' if device_id else ''}.")

    def next(self):
        self._api_request('POST', '/me/player/next')
        print("Siguiente pista.")

    def previous(self):
        self._api_request('POST', '/me/player/previous')
        print("Pista anterior.")

    def volume(self, vol):
        self._api_request('PUT', f'/me/player/volume?volume_percent={vol}')
        print(f"Volumen fijado a {vol}%.")

    def play_uri(self, uri, device_id=None):
        endpoint = '/me/player/play'
        if device_id:
            import time
            for _ in range(3):
                res = self._api_request('GET', '/me/player/devices')
                devs = res.get('devices', [])
                if any(d['id'] == device_id and d['is_active'] for d in devs):
                    break
                time.sleep(2)
            else:
                print("Error: device no estabilizado todavía", file=sys.stderr)
                sys.exit(1)
            endpoint += f"?device_id={device_id}"
        self._api_request('PUT', endpoint, payload={"uris": [uri]})
        print(f"Reproduciendo URI: {uri}{f' en {device_id}' if device_id else ''}")

    def transfer(self, device_id, force_play=True):
        payload = {"device_ids": [device_id], "play": force_play}
        self._api_request('PUT', '/me/player', payload=payload)
        import time
        time.sleep(2)
        print(f"Reproducción transferida al dispositivo {device_id}.")

    def search(self, query, limit=5):
        q = urllib.parse.quote(query)
        res = self._api_request('GET', f'/search?q={q}&type=track&limit={limit}')
        tracks = res.get('tracks', {}).get('items', [])
        if not tracks:
            print(f"No se encontraron resultados para: {query}")
            return
        print(f"Resultados para '{query}':")
        for i, t in enumerate(tracks):
            artists = ", ".join([a['name'] for a in t.get('artists', [])])
            print(f"{i+1}. {t['name']} - {artists} (URI: {t['uri']})")
        return tracks


def run_auth_server():
    client_id = get_env_var("SPOTIFY_CLIENT_ID", True)
    client_secret = get_env_var("SPOTIFY_CLIENT_SECRET", True)
    redirect_uri = get_env_var("SPOTIFY_REDIRECT_URI", True)
    
    scope = "user-read-playback-state user-modify-playback-state"
    auth_url = (
        "https://accounts.spotify.com/authorize?"
        + urllib.parse.urlencode({
            'response_type': 'code',
            'client_id': client_id,
            'scope': scope,
            'redirect_uri': redirect_uri
        })
    )
    print("=" * 60)
    print("SPOTIFY OAUTH BOOTSTRAP")
    print("=" * 60)
    print("1. Abre la siguiente URL en tu navegador:\n")
    print(auth_url)
    print("\n2. Autoriza la aplicación.")
    print("3. Serás redirigido a http://127.0.0.1:8888/callback")
    print("4. Esperando callback en puerto 8888...\n")

    class AuthHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress default logging

        def do_GET(self):
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            if 'code' not in params:
                self.wfile.write(b"Error: Code not found in URL.")
                return
            
            code = params['code'][0]
            self.wfile.write(b"<h2>Autorizacion exitosa!</h2><p>Revisa la terminal de Doctor-Lucy.</p>")
            self.wfile.flush()
            
            # Exchange code for token
            auth_string = f"{client_id}:{client_secret}"
            auth_b64 = base64.b64encode(auth_string.encode()).decode()
            data = urllib.parse.urlencode({
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }).encode()
            
            req = urllib.request.Request(
                'https://accounts.spotify.com/api/token',
                data=data,
                headers={
                    'Authorization': f'Basic {auth_b64}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            try:
                with urllib.request.urlopen(req) as resp:
                    res = json.loads(resp.read())
                    refresh_token = res.get('refresh_token')
                    
                    print("\n" + "=" * 60)
                    print("¡ÉXITO! Refresh token obtenido.")
                    print("Agrega la siguiente línea a tu archivo .env:\n")
                    print(f"SPOTIFY_REFRESH_TOKEN={refresh_token}")
                    print("=" * 60 + "\n")
            except urllib.error.HTTPError as e:
                print(f"Error obteniendo token: {e.read().decode()}", file=sys.stderr)
            
            # Ensure the server knows to stop
            sys.exit(0)
    
    try:
        server = HTTPServer(('127.0.0.1', 8888), AuthHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCancelado por el usuario.")
    except SystemExit:
        pass

def main():
    load_env()
    parser = argparse.ArgumentParser(description="Spotify v1 Controller CLI para Doctor-Lucy")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    subparsers.add_parser("auth", help="Inicia servidor local para obtener el REFRESH_TOKEN")
    subparsers.add_parser("status", help="Muestra el estado de reproducción actual")
    subparsers.add_parser("devices", help="Lista los dispositivos disponibles")
    play_parser = subparsers.add_parser("play", help="Reanuda la reproducción")
    play_parser.add_argument("--device", help="ID del dispositivo")

    pause_parser = subparsers.add_parser("pause", help="Pausa la reproducción")
    pause_parser.add_argument("--device", help="ID del dispositivo")

    subparsers.add_parser("next", help="Salta a la siguiente pista")
    subparsers.add_parser("previous", help="Vuelve a la pista anterior")
    
    transfer_parser = subparsers.add_parser("transfer", help="Transfiere la reproducción a un dispositivo")
    transfer_parser.add_argument("device_id", type=str, help="ID del dispositivo")
    transfer_parser.add_argument("--pause", action="store_false", dest="play", help="No iniciar reproducción tras transferencia")
    transfer_parser.set_defaults(play=True)
    
    vol_parser = subparsers.add_parser("volume", help="Ajusta el volumen (0-100)")
    vol_parser.add_argument("percent", type=int, help="Porcentaje de volumen (0-100)")
    
    uri_parser = subparsers.add_parser("play_uri", help="Reproduce una URI específica de Spotify")
    uri_parser.add_argument("uri", type=str, help="URI de Spotify (ej: spotify:track:...)")
    uri_parser.add_argument("--device", help="ID del dispositivo")

    search_parser = subparsers.add_parser("search", help="Busca canciones en Spotify")
    search_parser.add_argument("query", type=str, help="Término de búsqueda")
    search_parser.add_argument("--limit", type=int, default=5, help="Límite de resultados")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "auth":
        run_auth_server()
        return

    client = SpotifyClient()

    if args.command == "status":
        client.status()
    elif args.command == "devices":
        client.devices()
    elif args.command == "play":
        client.play(args.device)
    elif args.command == "pause":
        client.pause(args.device)
    elif args.command == "next":
        client.next()
    elif args.command == "previous":
        client.previous()
    elif args.command == "transfer":
        client.transfer(args.device_id, args.play)
    elif args.command == "volume":
        if 0 <= args.percent <= 100:
            client.volume(args.percent)
        else:
            print("El volumen debe estar entre 0 y 100", file=sys.stderr)
    elif args.command == "play_uri":
        client.play_uri(args.uri, args.device)
    elif args.command == "search":
        client.search(args.query, args.limit)

if __name__ == "__main__":
    main()
