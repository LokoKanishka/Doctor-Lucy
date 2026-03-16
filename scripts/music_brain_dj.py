import sys
import subprocess
import os
import urllib.parse

def stop_music():
    try:
        subprocess.run("pkill -f 'firefox.*youtube'", shell=True)
        return "🛑 Música detenida."
    except:
        return "No hay música sonando."

def play_music(query):
    try:
        print(f"🔍 Abriendo YouTube en Firefox (Enjambre): {query}...")
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        
        # Path absoluto del perfil Enjambre (evita el diálogo de Profile Manager)
        profile_path = "/home/lucy-ubuntu/snap/firefox/common/.mozilla/firefox/STX7CwNy.Perfil 2"
        # nohup + setsid para desvincular completamente Firefox del proceso padre
        cmd = f'nohup setsid firefox --no-remote --profile "{profile_path}" "{url}" > /dev/null 2>&1 &'
        os.system(cmd)
        return f"🎶 Abriendo en Firefox Enjambre (sin anuncios): {query}"
    except Exception as e:
        return f"💥 Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: music_brain_dj.py [play <query> | stop]")
        sys.exit(1)

    action = sys.argv[1].lower()
    
    if action == "play" and len(sys.argv) > 2:
        res = play_music(" ".join(sys.argv[2:]))
        print(res)
    elif action == "stop":
        res = stop_music()
        print(res)
    else:
        print("Acción no reconocida.")
