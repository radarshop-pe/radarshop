@echo off
echo.
echo  ====================================
echo   Radarshop - Panel de gestion
echo  ====================================
echo.

pip show flask >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo  Instalando dependencias por primera vez...
    pip install flask flask-cors openpyxl
    echo.
)

echo  Iniciando servidor...
echo  Abriendo en tu navegador: http://localhost:5000
echo.
echo  Para cerrar el servidor presiona CTRL+C
echo.

start "" http://localhost:5000
python app.py
pause
