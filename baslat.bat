@echo off
title Statistics Dashboard
echo Statistics Dashboard Baslatiliyor...
cd /d %~dp0
if not exist venv (
    echo HATA: Sanal ortam (venv) bulunamadi.
    pause
    exit /b
)
.\venv\Scripts\python.exe stats_dashboard.py
pause
