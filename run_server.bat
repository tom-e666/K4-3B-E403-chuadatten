@echo off
chcp 65001 > nul
echo =======================================================
echo 🚀 KHỞI ĐỘNG FEYNMAN AI SERVER (REVERSE TUTORING)
echo =======================================================

rem Dùng nhãn goto thay cho khối if (...) else (...): mọi dấu ngoặc đóng nằm trong
rem câu echo bên trong khối if đều bị cmd hiểu là kết thúc khối, gây lỗi
rem "... was unexpected at this time".
setlocal
set "LOCAL_VENV=%~dp0.venv\Scripts\python.exe"
set "LAB4_VENV=d:\vin20k\LAB4\K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs\starter_v0\.venv\Scripts\python.exe"

if exist "%LOCAL_VENV%" goto use_local
if exist "%LAB4_VENV%" goto use_lab4
goto use_system

:use_local
echo [INFO] Đang dùng Python từ môi trường ảo của dự án: .venv
set "PY_EXE=%LOCAL_VENV%"
goto run

:use_lab4
echo [INFO] Đang dùng Python từ môi trường ảo Lab 4
set "PY_EXE=%LAB4_VENV%"
goto run

:use_system
echo [INFO] Đang dùng Python hệ thống theo PATH
set "PY_EXE=python"
goto run

:run
cd /d "%~dp0"
echo [INFO] Server sẽ chạy tại http://localhost:8000 - mở đúng địa chỉ này, đừng mở thẳng file index.html
"%PY_EXE%" backend\server.py

pause
