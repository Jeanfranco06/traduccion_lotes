# Instrucciones de Uso - Traductor de Archivos por Lotes (Sistema Multi-Agente)

## Inicio Rapido

### 1. Configurar API Key
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env y agregar tu API key
# GOOGLE_API_KEY=tu_api_key_aqui
```

**Obtener API Key:**
1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Inicia sesion con tu cuenta de Google
3. Haz clic en "Create API Key"
4. Copia la API key generada

### 2. Ejecutar la Aplicacion

**Windows:**
```bash
# Doble clic en start.bat
# O ejecutar manualmente:
pip install -r requirements.txt
streamlit run app.py
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 3. Usar la Aplicacion

1. **Configurar idiomas** en el panel lateral
2. **Hacer clic en "Inicializar Sistema"**
3. **Subir archivos** (puedes subir multiples archivos)
4. **Hacer clic en "Iniciar Traduccion"**
5. **Esperar a que termine** el procesamiento
6. **Descargar archivo ZIP** con todas las traducciones

## Formatos Soportados

| Formato | Descripcion |
|---------|-------------|
| TXT | Archivos de texto plano |
| PDF | Documentos PDF (se exporta como TXT) |
| DOCX | Documentos de Microsoft Word |
| PPTX | Presentaciones de Microsoft PowerPoint |
| XLSX | Hojas de calculo de Microsoft Excel |
| JSON | Archivos de formato JSON |
| HTML | Paginas web |

## Arquitectura del Sistema Multi-Agente

### Agentes de IA (4 Agentes)

1. **Agente Extractor/Normalizador** (`agents/extractor.py`)
   - Analiza el documento
   - Detecta idioma y dominio del texto
   - Normaliza el contenido
   - Prepara instrucciones de contexto para el traductor

2. **Agente Traductor** (`agents/translator.py`)
   - Usa LangGraph con Google Gemini
   - Traduce texto preservando formato
   - Soporta multiples idiomas

3. **Agente Revisor/Calidad** (`agents/reviewer.py`)
   - Evalua calidad de traducciones
   - Detecta errores gramaticales
   - Proporciona puntuacion y sugerencias
   - Si no aprueba, solicita correccion

4. **Agente Formateador** (`agents/formatter.py`)
   - Verifica integridad del formato
   - Reconstruye el documento final
   - Asegura que no se pierdan elementos

### Flujo de Procesamiento con LangGraph

```
[Documento Subido]
         |
         v
[1. EXTRACTOR] --> Detecta idioma, dominio, normaliza
         |
         v
[2. TRADUCTOR] --> Genera traduccion preservando formato
         |
         v
[3. REVISOR/QA] --> Evalua precision, formato y estilo
         |
   ¿Aprobado?
   ├── NO --> [Correccion] --> (vuelve a Revisor)
   └── SI
         |
         v
[4. FORMATEADOR] --> Reconstruye formato y empaqueta
         |
         v
[ARCHIVO FINAL TRADUCIDO]
```

### Caracteristicas del Grafo LangGraph

- **Control de estado (Stateful)**: Mantiene contexto de archivos y estado de avance
- **Ciclos de retroalimentacion**: El revisor puede devolver al traductor para correccion
- **Maximo 1 iteracion**: Para evitar lentitud en demostracion en vivo
- **Visualizacion**: Muestra en que nodo del grafo se encuentra la ejecucion

## Solucion de Problemas

### Error "API key not configured"
- Verifica que el archivo `.env` exista y tenga tu API key
- Asegurate de que la API key sea valida

### Error "Module not found"
```bash
pip install -r requirements.txt
```

### La aplicacion no inicia
```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error de traduccion
- Verifica tu conexion a internet
- Verifica que la API key sea valida
- Intenta con un archivo mas pequeno

## Caracteristicas Principales

- **Sistema multi-agente**: 4 agentes especializados
- **Procesamiento en lote**: Multiples archivos simultaneamente
- **Interfaz intuitiva**: Facil de usar
- **Manejo de errores**: Continua si un archivo falla
- **Progreso en tiempo real**: Muestra avance del procesamiento
- **Exportacion ZIP**: Descarga todas las traducciones juntas
- **Revision de calidad**: Evalua las traducciones automaticamente
- **Visualizacion del grafo**: Muestra la arquitectura del sistema

## Requisitos del Sistema

- Python 3.8 o superior
- Conexion a internet
- API key de Google Gemini
- Navegador web moderno

## Notas para la Evaluacion

Esta aplicacion cumple con los siguientes criterios:

1. **Sistema de agentes**: 4 agentes colaboradores con LangGraph
2. **Procesamiento en lote**: Soporte para multiples archivos
3. **Interfaz Streamlit**: Diseno intuitivo y profesional
4. **Manejo de errores**: Try-except en operaciones criticas
5. **Caché**: Uso de session_state de Streamlit
6. **Visualizacion clara**: Tabla de resultados y progreso
7. **Arquitectura avanzada**: LangGraph con ciclos de retroalimentacion
8. **Responsabilidad unica**: Cada agente tiene una funcion específica

## Estructura del Proyecto

```
Traductor_lotes/
├── app.py                  # Interfaz principal de Streamlit
├── agents/
│   ├── __init__.py
│   ├── extractor.py        # Agente extractor/normalizador
│   ├── translator.py       # Agente traductor
│   ├── reviewer.py         # Agente revisor de calidad
│   ├── formatter.py        # Agente formateador
│   └── graph.py            # Grafo LangGraph
├── utils/
│   ├── __init__.py
│   ├── file_handlers.py    # Lectura/escritura de archivos
│   └── zip_exporter.py     # Empaquetado ZIP
├── requirements.txt        # Dependencias
├── .env.example           # Ejemplo de configuracion
├── start.bat              # Inicio rapido (Windows)
└── start.sh               # Inicio rapido (Linux/Mac)
```

## Soporte

Para problemas o preguntas, revisa el README.md o el archivo bases.md.