@echo off
title Smart Retail Sales Analytics & Multi-Store BI System
echo =====================================================================
echo Starting Smart Retail Sales Analytics & Visualization System...
echo =====================================================================
echo.

:: Ensure we are in the script's directory
cd /d "%~dp0"

echo [1/2] Checking local server configuration...
echo [2/2] Launching Streamlit on http://127.0.0.1:8501 ...
echo.

:: Launch Streamlit bound to 127.0.0.1 with CORS & XSRF disabled for reliable local connection
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.enableCORS false --server.enableXsrfProtection false

pause
