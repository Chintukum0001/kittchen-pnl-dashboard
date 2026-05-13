@echo off
title Kittchen P&L Dashboard Launcher
color 0A

echo =====================================================
echo   Kittchen Cloud Kitchen - P&L Dashboard Launcher
echo =====================================================
echo.

REM -- Check Python is installed -------------------------
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found.

REM -- Move to the folder where this script lives -------
cd /d "%~dp0"

REM -- Install / upgrade required packages --------------
echo.
echo Installing required packages (first run may take a minute)...
pip install streamlit pandas numpy plotly openpyxl --quiet --upgrade

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Package installation failed.
    echo Try running as Administrator, or run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Packages ready.

REM -- Check the data file is present -------------------
IF NOT EXIST "Kittchen PNL Data.xlsx" (
    echo.
    echo [ERROR] "Kittchen PNL Data.xlsx" not found in this folder.
    echo Please copy the data file here:
    echo   %~dp0
    pause
    exit /b 1
)

echo [OK] Data file found.

REM -- Launch Streamlit ----------------------------------
echo.
echo Starting dashboard... A browser tab will open automatically.
echo (To stop the dashboard, close this window or press Ctrl+C)
echo.

streamlit run kitchen_pnl_app.py --server.port 8501 --browser.gatherUsageStats false

pause
