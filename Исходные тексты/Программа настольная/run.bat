@echo off
chcp 65001 >nul
python app.py
if errorlevel 1 pause
