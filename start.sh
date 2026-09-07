#!/bin/bash

echo "========================================"
echo "Traductor de Archivos por Lotes"
echo "========================================"
echo

# Verificar si Python está instalado
if ! command -v python &> /dev/null; then
    echo "ERROR: Python no está instalado"
    echo "Por favor instala Python desde https://python.org"
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip &> /dev/null; then
    echo "ERROR: pip no está instalado"
    echo "Ejecuta: python -m ensurepip --upgrade"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Verificar si existe .env
if [ ! -f ".env" ]; then
    echo
    echo "AVISO: No se encontró archivo .env"
    echo "Copia .env.example como .env y configura tu API key"
    echo
fi

# Ejecutar la aplicación
echo
echo "Iniciando aplicación Streamlit..."
streamlit run app.py