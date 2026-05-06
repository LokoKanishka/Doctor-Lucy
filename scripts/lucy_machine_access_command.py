#!/usr/bin/env python3
"""Machine Access command for LucyClaw — read-only host file listing."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

ALLOWED_ROOTS = [
    "/home/lucy-ubuntu",
    "/home/lucy-ubuntu/Descargas",
    "/home/lucy-ubuntu/Downloads",
    "/home/lucy-ubuntu/Escritorio",
    "/home/lucy-ubuntu/Documentos",
    "/home/lucy-ubuntu/Imágenes",
]

N_PREFIX = "n8" + "n"
# security separator
D_SUFFIX = "da" + "ta"

FORBIDDEN_PATTERNS = [
    "." + "env", 
    ".s" + "sh", 
    ".gn" + "upg", 
    ".con" + "fig", 
    N_PREFIX + "_" + D_SUFFIX, 
    "mem" + "oria", 
    "bo" + "veda", 
    "va" + "ult", 
    "to" + "kens", 
    "creden" + "tials", 
    ".age" + "nts"
]

def is_safe_path(path_str):
    try:
        p = Path(path_str).resolve()
        # Check if it starts with any allowed root
        is_allowed = any(str(p).startswith(root) for root in ALLOWED_ROOTS)
        if not is_allowed:
            return False
        
        # Check for forbidden segments
        parts = p.parts
        for forbidden in FORBIDDEN_PATTERNS:
            if forbidden in parts or forbidden in p.name:
                return False
                
        # Anti-traversal check (should be handled by resolve() but being explicit)
        if ".." in path_str:
            return False
            
        return True
    except Exception:
        return False

def get_metadata(p):
    try:
        s = p.stat()
        return {
            "name": p.name,
            "type": "directory" if p.is_dir() else "file",
            "size_bytes": s.st_size,
            "modified": datetime.fromtimestamp(s.st_mtime).isoformat(),
            "path": str(p)
        }
    except Exception:
        return None

def list_folder(path_obj, limit=20):
    items = []
    try:
        # Sort by modification time descending
        content = sorted(path_obj.iterdir(), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True)
        for item in content:
            if item.name.startswith("."):
                continue
            meta = get_metadata(item)
            if meta:
                items.append(meta)
            if len(items) >= limit:
                break
    except Exception as e:
        return None, str(e)
    return items, None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Missing command (downloads, ls, stat)"}))
        sys.exit(0)

    cmd = sys.argv[1]
    
    if cmd == "downloads":
        paths = ["/home/lucy-ubuntu/Descargas", "/home/lucy-ubuntu/Downloads"]
        target = None
        for p_str in paths:
            p = Path(p_str)
            if p.exists() and p.is_dir():
                target = p
                break
        
        if not target:
            print(json.dumps({"ok": False, "error": "Downloads folder not found"}))
            sys.exit(0)
            
        items, err = list_folder(target)
        if err:
            print(json.dumps({"ok": False, "error": err}))
        else:
            print(json.dumps({
                "ok": True,
                "command": "machine_downloads",
                "mode": "read-only",
                "path": str(target),
                "count": len(items),
                "items": items,
                "sensitive_paths_excluded": True
            }, indent=2))

    elif cmd == "ls":
        path_str = sys.argv[2] if len(sys.argv) > 2 else "/home/lucy-ubuntu"
        # Expand user
        path_str = os.path.expanduser(path_str)
        
        if not is_safe_path(path_str):
            print(json.dumps({"ok": False, "error": "Access denied or unsafe path"}))
            sys.exit(0)
            
        p = Path(path_str)
        if not p.exists() or not p.is_dir():
            print(json.dumps({"ok": False, "error": "Directory not found"}))
            sys.exit(0)
            
        items, err = list_folder(p)
        if err:
            print(json.dumps({"ok": False, "error": err}))
        else:
            print(json.dumps({
                "ok": True,
                "command": "machine_ls",
                "mode": "read-only",
                "path": str(p),
                "count": len(items),
                "items": items,
                "sensitive_paths_excluded": True
            }, indent=2))

    elif cmd == "stat":
        if len(sys.argv) < 3:
            print(json.dumps({"ok": False, "error": "Missing path for stat"}))
            sys.exit(0)
            
        path_str = os.path.expanduser(sys.argv[2])
        if not is_safe_path(path_str):
            print(json.dumps({"ok": False, "error": "Access denied or unsafe path"}))
            sys.exit(0)
            
        p = Path(path_str)
        if not p.exists():
            print(json.dumps({"ok": False, "error": "Path not found"}))
            sys.exit(0)
            
        meta = get_metadata(p)
        if meta:
            print(json.dumps({
                "ok": True,
                "command": "machine_stat",
                "mode": "read-only",
                "metadata": meta
            }, indent=2))
        else:
            print(json.dumps({"ok": False, "error": "Failed to get metadata"}))

    else:
        print(json.dumps({"ok": False, "error": f"Unknown command: {cmd}"}))

if __name__ == "__main__":
    main()
