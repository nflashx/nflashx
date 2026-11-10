@echo off
cd /d "%~dp0"
start "" /min "C:\Users\Noway\miniconda3\python.exe" -I server.py
start "" http://127.0.0.1:8600/admin.html
