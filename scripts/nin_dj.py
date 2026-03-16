import sys
import os

if __name__ == "__main__":
    print("WARNING: This script has been deprecated. Please use music_brain_dj.py instead.")
    
    # Try to pass execution to the new script if called natively
    args = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    os.system(f"python3 '/home/lucy-ubuntu/Escritorio/doctor de lucy/scripts/music_brain_dj.py' {args}")
