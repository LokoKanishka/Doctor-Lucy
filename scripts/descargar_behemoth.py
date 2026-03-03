import os
from huggingface_hub import hf_hub_download, list_repo_files

REPO_ID = "bartowski/TheDrummer_Behemoth-X-123B-v2-GGUF"
SEARCH_PATTERN = "TheDrummer_Behemoth-X-123B-v2-Q4_K_M"
DOWNLOAD_DIR = "/home/lucy-ubuntu/Escritorio/Modelos_Descargados_GGUF"

# Crear directorio si no existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

print(f"Buscando archivos en {REPO_ID} que contengan '{SEARCH_PATTERN}'...")

try:
    # Obtener lista de todos los archivos
    files = list_repo_files(repo_id=REPO_ID)
    
    # Filtrar solo los que nos interesan
    target_files = [f for f in files if SEARCH_PATTERN in f and f.endswith('.gguf')]
    
    if not target_files:
        print(f"ERROR: No se encontraron archivos que coincidan.")
    else:
        print(f"Se encontraron {len(target_files)} archivos para descargar:")
        for f in target_files:
            print(f" - {f}")
        
        print("\nComenzando descarga (esto tomará mucho tiempo)...")
        for f in target_files:
            print(f" Descargando: {f}")
            downloaded_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=f,
                local_dir=DOWNLOAD_DIR,
                local_dir_use_symlinks=False
            )
            print(f" ✓ Guardado en: {downloaded_path}")
            
        print("\n¡Descarga de todas las partes completada con éxito!")

except Exception as e:
    print(f"Error durante el proceso: {e}")
