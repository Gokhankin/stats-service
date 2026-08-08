#!/bin/bash
echo "Statistics Dashboard Baslatiliyor..."
cd "$(dirname "$0")"
source ./venv/bin/activate
python3 stats_dashboard.py
