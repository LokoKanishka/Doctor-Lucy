#!/bin/bash

# Doctor Lucy - System Health Check Script
# Identifies zombie processes and high CPU usage.

echo "--- Doctor Lucy: Health Check ---"
date

echo -e "\n[1] Zombie Processes:"
ZOMBIES=$(ps -ef | grep defunct | grep -v grep)
if [ -z "$ZOMBIES" ]; then
    echo "No zombie processes found."
else
    echo "WARNING: Zombie processes found!"
    echo "$ZOMBIES"
fi

echo -e "\n[2] High CPU usage (Top 5):"
ps -eo pcpu,pid,user,comm --sort=-pcpu | head -n 6

echo -e "\n[3] Memory Status:"
free -h

echo -e "\n[4] Disk space on root (Summary):"
df -h / | tail -n 1

echo -e "\n--- End of Health Check ---"
