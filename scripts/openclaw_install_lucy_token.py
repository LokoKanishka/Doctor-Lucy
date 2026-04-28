#!/usr/bin/env python3
import os
import json
import shutil
import hashlib
import getpass
import datetime

def main():
    print("=== Instalador Seguro de Service Token Clawbot ===")
    token = getpass.getpass("Ingrese el Service Token (no se mostrará): ").strip()
    
    if not token:
        print("Error: El token no puede estar vacío.")
        return
        
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.expanduser("~/.openclaw")
    backup_dir = os.path.join(base_dir, "backups-tramo9.5")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    token_file = os.path.join(base_dir, "lucy-bridge-token")
    config_file = os.path.join(base_dir, "openclaw.json")
    
    backups = []
    
    if os.path.exists(token_file):
        bkp1 = os.path.join(backup_dir, f"lucy-bridge-token.bak.{stamp}")
        shutil.copy2(token_file, bkp1)
        backups.append(bkp1)
        
    if os.path.exists(config_file):
        bkp2 = os.path.join(backup_dir, f"openclaw.json.bak.{stamp}")
        shutil.copy2(config_file, bkp2)
        backups.append(bkp2)
        
    # Write token file securely
    # ensure file doesn't exist to set proper permissions cleanly, or open with fd
    with os.fdopen(os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f:
        f.write(token + "\n")
        
    # Update config
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        config = {}
        
    if "gateway" not in config:
        config["gateway"] = {}
    if "auth" not in config["gateway"]:
        config["gateway"]["auth"] = {}
        
    config["gateway"]["auth"]["mode"] = "token"
    config["gateway"]["auth"]["token"] = token
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
        
    # Hash of token for verification
    token_bytes = token.encode('utf-8')
    sha_12 = hashlib.sha256(token_bytes).hexdigest()[:12]
    
    print("\n[ÉXITO] Token instalado correctamente.")
    print("Backups creados:")
    for b in backups:
        print(f"  - {b}")
    print(f"Archivos actualizados: {token_file}, {config_file}")
    print(f"Token SHA256 (primeros 12): {sha_12}")
    
    print("\nPara validar el token, ejecute:")
    print("systemctl --user restart openclaw-gateway.service")
    print("OPENCLAW_BRIDGE_MODE=http python3 scripts/lucy_openclaw_bridge.py \"ping diagnóstico seguro: respondé solo OK\" --agent main")

if __name__ == "__main__":
    main()
