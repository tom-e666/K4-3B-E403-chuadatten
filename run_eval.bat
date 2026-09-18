@echo off
chcp 65001 > nul
echo =======================================================
echo 🧪 CHẠY KIỂM THỬ GOLDEN SET EVALUATION (MỤC §7 SPEC)
echo =======================================================

set LOCAL_VENV=%~dp0.venv\Scripts\python.exe
set LAB4_VENV=d:\vin20k\LAB4\K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs\starter_v0\.venv\Scripts\python.exe

if exist "%LOCAL_VENV%" (
    "%LOCAL_VENV%" eval\run_eval.py
) else if exist "%LAB4_VENV%" (
    "%LAB4_VENV%" eval\run_eval.py
) else (
    python eval\run_eval.py
)

pause
