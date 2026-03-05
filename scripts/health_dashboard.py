import os
import subprocess
import json
import datetime
import sqlite3
import pathlib

# Configuración de Rutas
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
OUTPUT_PATH = PROJECT_ROOT / "docs" / "dashboard.html"
BOVEDA_PATH = PROJECT_ROOT / "n8n_data" / "boveda_lucy.sqlite"
AGENTE_DB_PATH = PROJECT_ROOT / "memoria" / "agente_memoria.db"

def get_bash_output(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
    except:
        return "N/A"

def get_kg_stats():
    if not AGENTE_DB_PATH.exists(): return {}
    conn = sqlite3.connect(str(AGENTE_DB_PATH))
    stats = {}
    try:
        stats['entidades'] = conn.execute("SELECT COUNT(*) FROM kg_entidades").fetchone()[0]
        stats['relaciones'] = conn.execute("SELECT COUNT(*) FROM kg_relaciones").fetchone()[0]
        stats['observaciones'] = conn.execute("SELECT COUNT(*) FROM kg_observaciones").fetchone()[0]
    except:
        stats = {"note": "KG error"}
    conn.close()
    return stats

def generate_html():
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Recolectar datos Hardware
    cpu = get_bash_output("lscpu | grep 'Model name' | cut -d: -f2").strip()
    ram = get_bash_output("free -h | grep Mem | awk '{print $3 \" / \" $2}'")
    gpu = get_bash_output("nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu --format=csv,noheader,nounits")
    uptime = get_bash_output("uptime -p")
    
    # Recolectar datos Lucy
    kg = get_kg_stats()
    n8n_status = "ONLINE" if "200" in get_bash_output("curl -I -s http://localhost:6969/healthz | grep 200") else "OFFLINE"
    
    gpu_data = gpu.split(",") if gpu != "N/A" else ["N/A", "0", "0"]
    gpu_name = gpu_data[0]
    gpu_temp = gpu_data[1] if len(gpu_data) > 1 else "0"
    gpu_util = gpu_data[2] if len(gpu_data) > 2 else "0"

    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctora Lucy - Health Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f111a;
            --glass: rgba(255, 255, 255, 0.05);
            --border: rgba(255, 255, 255, 0.1);
            --accent: #00f2fe;
            --accent-2: #4facfe;
            --text: #e0e0e0;
            --text-muted: #a0a0a0;
            --success: #00ff88;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            background: var(--bg);
            background: radial-gradient(circle at top right, #1a1e2e, #0f111a);
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        header {{
            width: 100%;
            max-width: 1200px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(to right, var(--accent), var(--accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }}

        .status-badge {{
            padding: 0.5rem 1rem;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 20px;
            font-size: 0.9rem;
            color: var(--success);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .dot {{
            width: 10px;
            height: 10px;
            background: var(--success);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--success);
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.5; }}
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            width: 100%;
            max-width: 1200px;
        }}

        .card {{
            background: var(--glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 2rem;
            transition: transform 0.3s ease, border-color 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
            border-color: var(--accent);
        }}

        .card h2 {{
            font-size: 1.2rem;
            color: var(--text-muted);
            margin-bottom: 1.5rem;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        .val {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .sub {{
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .progress-container {{
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.05);
            border-radius: 3px;
            margin: 1rem 0;
            overflow: hidden;
        }}

        .progress-bar {{
            height: 100%;
            background: linear-gradient(to right, var(--accent), var(--accent-2));
            border-radius: 3px;
        }}

        .stats-list {{
            list-style: none;
        }}

        .stats-list li {{
            display: flex;
            justify-content: space-between;
            padding: 0.8rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        .stats-list li:last-child {{ border: 0; }}

        footer {{
            margin-top: 3rem;
            color: var(--text-muted);
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <header>
        <div>
            <h1>DOCTORA LUCY</h1>
            <p style="color: var(--text-muted)">Health & Intelligence Dashboard</p>
        </div>
        <div class="status-badge">
            <div class="dot"></div>
            SYSTEM OPERATIONAL
        </div>
    </header>

    <div class="grid">
        <div class="card">
            <h2>Hardware Core</h2>
            <div class="val">{gpu_name}</div>
            <div class="sub">CPU: {cpu}</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {gpu_util}%"></div>
            </div>
            <div class="sub">GPU Load: {gpu_util}% | Temp: {gpu_temp}°C</div>
        </div>

        <div class="card">
            <h2>Memoria Sistema</h2>
            <div class="val">{ram}</div>
            <div class="sub">Uptime: {uptime}</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: 45%"></div>
            </div>
            <div class="sub">DDR5 High Speed Memory</div>
        </div>

        <div class="card">
            <h2>Lucy Intelligence</h2>
            <ul class="stats-list">
                <li><span>Knowledge Graph</span> <strong>{kg.get('entidades', 0)} entidades</strong></li>
                <li><span>Relaciones Neuronales</span> <strong>{kg.get('relaciones', 0)} aristas</strong></li>
                <li><span>n8n Orchestrator</span> <strong style="color: var(--success)">{n8n_status}</strong></li>
                <li><span>Bóveda Local</span> <strong>ACTIVE</strong></li>
            </ul>
        </div>
    </div>

    <footer>
        Actualizado: {ahora} | Fingerprint: DOCTOR_LUCY__7X9K
    </footer>
</body>
</html>
    """
    
    # Crear carpeta docs si no existe
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"✅ Dashboard generado exitosamente en: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_html()
