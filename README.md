# Traductor de Archivos por Lotes

Aplicación web para traducción masiva de archivos usando agentes de IA con LangChain y Google Gemini.

## Características

- **Procesamiento en lote**: Sube múltiples archivos de diferentes formatos
- **Agentes de IA**: Sistema de traducción + revisión de calidad
- **Múltiples formatos**: TXT, PDF, DOCX, PPTX, Excel, JSON, HTML
- **Interfaz intuitiva**: Panel de control con progreso en tiempo real
- **Exportación ZIP**: Descarga todas las traducciones en un solo archivo

## Requisitos

- Python 3.8 o superior
- API Key de Google Gemini (obtener en [Google AI Studio](https://aistudio.google.com/app/apikey))

## Instalación

### Windows

1. Doble clic en `start.bat`
2. Seguir las instrucciones en pantalla

### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

### Instalación manual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env con tu API key

# Ejecutar aplicación
streamlit run app.py
```

## Uso

1. **Configurar API Key**: En el panel lateral, ingresa tu API key de Google Gemini
2. **Seleccionar idiomas**: Elige idioma origen y destino
3. **Inicializar agentes**: Haz clic en "Inicializar Agentes"
4. **Subir archivos**: Arrastra o selecciona los archivos a traducir
5. **Traducir**: Haz clic en "Iniciar Traducción"
6. **Descargar**: Exporta las traducciones en formato ZIP

## Estructura del Proyecto

```
Traductor_lotes/
├── app.py                  # Interfaz principal de Streamlit
├── agents/
│   ├── __init__.py
│   ├── translator.py       # Agente traductor
│   └── reviewer.py         # Agente de control de calidad
├── utils/
│   ├── __init__.py
│   ├── file_handlers.py    # Lectura/escritura de archivos
│   └── zip_exporter.py     # Empaquetado ZIP
├── requirements.txt        # Dependencias
├── .env.example           # Ejemplo de configuración
├── start.bat              # Inicio rápido (Windows)
└── start.sh               # Inicio rápido (Linux/Mac)
```

## Formatos Soportados

| Formato | Lectura | Escritura |
|---------|---------|-----------|
| TXT | ✅ | ✅ |
| PDF | ✅ | ✅ (como TXT) |
| DOCX | ✅ | ✅ |
| PPTX | ✅ | ✅ |
| XLSX | ✅ | ✅ |
| JSON | ✅ | ✅ |
| HTML | ✅ | ✅ |

## Solución de Problemas

### Error "API key not configured"
- Verifica que hayas creado el archivo `.env` con tu API key
- Asegúrate de que la API key sea válida

### Error "Module not found"
- Ejecuta `pip install -r requirements.txt`
- Verifica que el entorno virtual esté activado

### La aplicación no inicia
- Verifica que Streamlit esté instalado: `pip install streamlit`
- Ejecuta manualmente: `streamlit run app.py`

## Licencia

Proyecto educativo - Uso libre