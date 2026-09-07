@echo off
echo ========================================
echo Traductor de Archivos por Lotes
echo ========================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

:: Verificar si pip está instalado
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no está instalado
    echo Ejecuta: python -m ensurepip --upgrade
    pause
    exit /b 1
)

:: Instalar dependencias si no existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

:: Verificar si existe .env
if not exist ".env" (
    echo.
    echo AVISO: No se encontró archivo .env
    echo Copia .env.example como .env y configura tu API key
    echo.
    pause
)

:: Ejecutar la aplicación
echo.
echo Iniciando aplicación Streamlit...
streamlit run app.py

pause