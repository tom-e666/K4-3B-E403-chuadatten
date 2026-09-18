@echo off
chcp 65001 >nul

echo =======================================================
echo GOLDEN SET EVALUATION
echo =======================================================

set "LOCAL_VENV=%~dp0.venv\Scripts\python.exe"
set "LAB4_VENV=D:\vin20k\LAB4\K4-L3B-Day04-Prompt-Engineering-Tool-Calling-Labs\starter_v0\.venv\Scripts\python.exe"

if exist "%LOCAL_VENV%" (
    echo Using local virtual environment...
    "%LOCAL_VENV%" "%~dp0eval\run_eval.py"
) else (
    if exist "%LAB4_VENV%" (
        echo Using LAB4 virtual environment...
        "%LAB4_VENV%" "%~dp0eval\run_eval.py"
    ) else (
        echo Using system Python...
        python "%~dp0eval\run_eval.py"
    )
)

echo.
echo =======================================================
echo EVALUATION FINISHED
echo =======================================================

pause