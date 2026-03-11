#!/usr/bin/env bash
set -euo pipefail

# Doctor Lucy - Disk Cleanup Utility
# Identifies space-consuming targets for cleanup.

echo "--- Doctor Lucy: Disk Cleanup ---"
date

echo -e "\n[1] Largest directories in /home (Top 5):"
du -ah "$HOME" --max-depth=1 2>/dev/null | sort -hr | head -n 5

echo -e "\n[2] APT Cache size:"
du -sh /var/cache/apt/archives 2>/dev/null

echo -e "\n[3] Suggested Actions:"
echo "- Consider running 'sudo apt autoremove' to clear unused packages."
echo "- Consider running 'sudo apt clean' to clear the apt cache."
echo "- Review large files in the Desktop (Escritorio) listed above."

echo -e "\n--- End of Cleanup Utility ---"
