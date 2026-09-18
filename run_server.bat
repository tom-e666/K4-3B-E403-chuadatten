@echo off
chcp 65001 > nul
echo =======================================================
echo 🚀 KHỞI ĐỘNG FEYNMAN AI SERVER (REVERSE TUTORING)
echo =======================================================

set LOCAL_VENV=%~dp0.venv\Scripts\python.exe
set LAB4_VENV=d:\vin20k\LAB4\K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs\starter_v0\.venv\Scripts\python.exe

if exist "%LOCAL_VENV%" (
    echo [INFO] Đang dùng Python từ môi trường ảo dự án (.venv)...
    "%LOCAL_VENV%" backend\server.py
) else if exist "%LAB4_VENV%" (
    echo [INFO] Đang dùng Python từ môi trường ảo Lab 4...
    "%LAB4_VENV%" backend\server.py
) else (
    echo [INFO] Đang dùng Python hệ thống...
    python backend\server.py
)

pause
