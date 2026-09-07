import streamlit as st
import os
import tempfile
from typing import Dict, Any, List
from dotenv import load_dotenv
import time

import logging
import warnings

# Silenciar logs ruidosos de librerías secundarias en la consola
logging.getLogger("fontTools").setLevel(logging.WARNING)
logging.getLogger("pdf2docx").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", message=".*fitz API is deprecated.*")
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

# Importar modulos del proyecto
from agents.graph import TranslationGraph
from utils.file_handlers import FileHandler
from utils.zip_exporter import ZipExporter

# Configuracion de la pagina
st.set_page_config(
    page_title="Traductor de Archivos por Lotes - Multi-Agente",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar variables de entorno
load_dotenv()

# Inicializar sesion de Streamlit
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = []
if 'translation_graph' not in st.session_state:
    st.session_state.translation_graph = None
if 'translated_chunks_progress' not in st.session_state:
    st.session_state.translated_chunks_progress = {}


def initialize_graph(api_key: str, source_lang: str, target_lang: str, model_name: str = "gemini-3.5-flash"):
    """Inicializa el grafo de traduccion multi-agente."""
    try:
        st.session_state.translation_graph = TranslationGraph(api_key=api_key, model_name=model_name)
        st.session_state.source_lang = source_lang
        st.session_state.target_lang = target_lang
        return True
    except Exception as e:
        st.error(f"Error al inicializar grafo: {e}")
        return False


def process_file_with_graph(file_data: Dict[str, Any], graph: TranslationGraph,
                           source_lang: str, target_lang: str,
                           progress_callback=None,
                           translated_chunks_cache: List[str] = None,
                           translate_references: bool = False) -> Dict[str, Any]:
    """
    Procesa un archivo usando el grafo de 4 agentes.
    
    Returns:
        Diccionario con resultados del procesamiento
    """
    # Extraer texto plano del contenido para mostrar
    original_content = file_data.get('content', '')
    if isinstance(original_content, dict):
        if 'paragraphs' in original_content:
            original_text = '\n\n'.join([p.get('text', '') for p in original_content.get('paragraphs', [])])
        else:
            original_text = str(original_content) if original_content else ''
    elif isinstance(original_content, list):
        original_text = '\n'.join([str(item) for item in original_content])
    elif isinstance(original_content, str):
        original_text = original_content
    else:
        original_text = str(original_content) if original_content else ''
    
    result = {
        'name': file_data.get('name', 'unknown'),
        'extension': file_data.get('extension', ''),
        'docx_path': file_data.get('docx_path'),
        'original_file_path': file_data.get('original_file_path'),
        'status': 'procesando',
        'original_content': original_content,
        'original_text': original_text,
        'translated_content': None,
        'final_content': None,
        'step_history': [],
        'error': None
    }
    
    steps = ['extractor', 'translator', 'reviewer', 'formatter']
    
    try:
        # Ejecutar grafo de traduccion
        graph_result = graph.translate_document(
            file_name=file_data['name'],
            file_extension=file_data['extension'],
            original_content=file_data['content'],
            source_language=source_lang,
            target_language=target_lang,
            max_iterations=1,
            progress_callback=progress_callback,
            docx_path=file_data.get('docx_path'),
            translated_chunks_cache=translated_chunks_cache,
            translate_references=translate_references
        )
        
        result['translated_content'] = graph_result.get('translated_content')
        result['final_content'] = graph_result.get('final_content')
        result['step_history'] = graph_result.get('step_history', [])
        result['status'] = graph_result.get('status', 'completado')
        result['review'] = graph_result.get('review_result')
        result['extraction'] = graph_result.get('extraction_result')
        result['translated_chunks_cache'] = graph_result.get('translated_chunks_cache', [])
        result['references_text'] = graph_result.get('references_text')
        
        # Pre-generar el PDF estructurado una sola vez al finalizar
        if file_data.get('extension', '').lower() == '.pdf':
            docx_path = file_data.get('docx_path')
            out_docx = docx_path.replace('.docx', '_traducido.docx') if docx_path else None
            if out_docx and os.path.exists(out_docx):
                # Optimizar layout: eliminar watermarks, comprimir espacios, bordes en tablas
                FileHandler.optimize_translated_docx(out_docx, out_docx)
                pdf_path = FileHandler.docx_to_pdf(out_docx)
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, 'rb') as pf:
                        result['pdf_bytes'] = pf.read()
                    result['pdf_path'] = pdf_path

        
        if graph_result.get('error'):
            result['error'] = graph_result['error']
            
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
    
    return result


def main():
    st.title("🌐 Traductor de Archivos por Lotes - Sistema Multi-Agente")
    st.markdown("---")
    
    # Sidebar para configuracion
    with st.sidebar:
        st.header("⚙️ Configuracion")
        
        # API Key
        api_key = st.text_input(
            "API Key de Google Gemini",
            type="password",
            help="Ingresa tu API key de Google AI Studio"
        )
        
        # Idiomas
        languages = {
            'es': 'Espanol',
            'en': 'Ingles',
            'fr': 'Frances',
            'de': 'Aleman',
            'it': 'Italiano',
            'pt': 'Portugues',
            'zh': 'Chino',
            'ja': 'Japones'
        }
        
        source_lang = st.selectbox(
            "Idioma origen",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0
        )
        
        target_lang = st.selectbox(
            "Idioma destino",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=1
        )
        
        # Selector de modelo
        st.markdown("---")
        st.subheader("🤖 Modelo de IA")
        
        models = {
            'gemini-3.5-flash': 'Gemini 3.5 Flash (Recomendado - buen equilibrio calidad/costo)',
            'gemini-3.6-flash': 'Gemini 3.6 Flash (Calidad superior, cuota más limitada)',
            'gemini-3.5-flash-lite': 'Gemini 3.5 Flash-Lite (Máxima cuota gratuita, menor calidad)'
        }
        
        selected_model = st.selectbox(
            "Seleccionar modelo",
            options=list(models.keys()),
            format_func=lambda x: models[x],
            index=0,
            help="Flash ofrece el mejor equilibrio. Flash-Lite prioriza la cuota gratuita."
        )
        
        st.session_state.selected_model = selected_model
        
        # Opción: traducir referencias bibliográficas
        st.markdown("---")
        st.subheader("📚 Referencias bibliográficas")
        translate_references = st.checkbox(
            "Traducir también las referencias",
            value=False,
            help="Si está desmarcado (recomendado), las referencias se mantienen en su idioma original para no alterar nombres ni citas."
        )
        st.session_state.translate_references = translate_references
        
        # Boton de inicializacion
        if st.button("🔧 Inicializar Sistema", width='stretch'):
            if api_key:
                model_to_use = st.session_state.get('selected_model', 'gemini-3.5-flash')
                if initialize_graph(api_key, source_lang, target_lang, model_to_use):
                    st.success(f"✅ Sistema inicializado con modelo: {model_to_use}")
            else:
                st.warning("⚠️ Por favor ingresa una API key")
        
        st.markdown("---")
        st.markdown("### 🤖 Agentes del Sistema")
        st.markdown("""
        1. **Extractor**: Analiza y normaliza
        2. **Traductor**: Genera traduccion
        3. **Revisor**: Evalua calidad
        4. **Formateador**: Reconstruye formato
        """)
        
        st.markdown("---")
        st.markdown("### 📋 Formatos soportados")
        st.markdown("""
        - TXT, PDF, DOCX
        - PPTX, XLSX
        - JSON, HTML
        """)
    
    # Mostrar arquitectura del grafo
    if st.session_state.translation_graph:
        st.markdown("---")
        with st.expander("🔍 Arquitectura del Sistema Multi-Agente", expanded=False):
            model_name = st.session_state.get('selected_model', 'gemini-3.5-flash')
            st.info(f"🤖 Modelo activo: **{model_name}**")
            st.code(st.session_state.translation_graph.get_graph_visualization(), language=None)
    
    # Contenido principal
    if not st.session_state.translation_graph:
        st.info("👈 Configura la API key y los idiomas en el panel lateral para comenzar")
        st.markdown("""
        ### 🚀 Cómo usar:
        1. Ingresa tu API key de Google Gemini
        2. Selecciona los idiomas origen y destino
        3. Haz clic en "Inicializar Sistema"
        4. Sube uno o mas archivos para traducir
        5. Descarga el archivo ZIP con las traducciones
        
        ### 🤖 Arquitectura Multi-Agente:
        - **Extractor**: Analiza idioma, dominio y normaliza el texto
        - **Traductor**: Genera la traduccion preservando formato
        - **Revisor**: Evalua calidad y detecta errores
        - **Formateador**: Reconstruye el formato final
        
        El sistema incluye ciclos de retroalimentacion para mejorar la calidad.
        """)
        return
    
    # Seccion de carga de archivos
    st.header("📂 Subir Archivos")
    uploaded_files = st.file_uploader(
        "Selecciona los archivos a traducir",
        type=['txt', 'pdf', 'docx', 'pptx', 'xlsx', 'xls', 'json', 'html'],
        accept_multiple_files=True,
        help="Puedes subir multiples archivos de diferentes formatos"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivo(s) subido(s)")
        
        # Mostrar archivos subidos
        with st.expander("📋 Ver archivos subidos", expanded=False):
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.type})")
        
        # Boton de procesamiento
        if st.button("🚀 Iniciar Traduccion", type="primary", width='stretch'):
            st.session_state.processing = True
            st.session_state.results = []
            
            # Barra de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Funcion de callback para progreso
            step_names = {
                'extractor': 'Analizando documento...',
                'translator': 'Traduciendo contenido...',
                'reviewer': 'Revisando calidad...',
                'formatter': 'Formateando resultado...'
            }
            
            def update_progress(step_name, progress, chunk_info=None):
                base_progress = (i / len(uploaded_files)) if uploaded_files else 0
                file_weight = 1.0 / len(uploaded_files) if uploaded_files else 1.0
                total_progress = base_progress + (progress * file_weight)
                progress_bar.progress(min(total_progress, 1.0))
                
                chunk_text = ""
                if chunk_info:
                    chunk_text = f" | Chunk {chunk_info['current']}/{chunk_info['total']}"
                
                model_display = st.session_state.get('selected_model', 'gemini-3.5-flash')
                status_text.text(f"Procesando: {file.name}{chunk_text} [{model_display}] - {step_names.get(step_name, 'Procesando...')}")
                
                # Guardar progreso de chunks en session_state
                if step_name == 'translator' and chunk_info:
                    if file.name not in st.session_state.translated_chunks_progress:
                        st.session_state.translated_chunks_progress[file.name] = {
                            'total_chunks': chunk_info['total'],
                            'completed_chunks': chunk_info['current'] - 1,
                            'status': 'procesando'
                        }
                    else:
                        st.session_state.translated_chunks_progress[file.name]['completed_chunks'] = chunk_info['current'] - 1
            
            # Procesar cada archivo
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Procesando: {file.name} ({i+1}/{len(uploaded_files)})")
                
                # Guardar archivo temporalmente
                tmp_path = None
                try:
                    # Guardar archivo temporalmente
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                        tmp.write(file.getvalue())
                        tmp_path = tmp.name
                    
                    # Leer archivo
                    file_data = FileHandler.read_file(tmp_path)
                    
                    # Usar el nombre original del archivo, no el del temporal
                    file_data['name'] = file.name
                    
                    # Agregar informacion de conversion PDF si existe
                    if file_data.get('docx_path'):
                        file_data['is_pdf_conversion'] = True
                    
                    # Obtener cache existente si hay reanudación
                    existing_cache = st.session_state.translated_chunks_progress.get(file.name, {}).get('chunks_cache', [])
                    
                    # Procesar con grafo de agentes
                    result = process_file_with_graph(
                        file_data,
                        st.session_state.translation_graph,
                        st.session_state.source_lang,
                        st.session_state.target_lang,
                        progress_callback=update_progress,
                        translated_chunks_cache=existing_cache if existing_cache else None,
                        translate_references=st.session_state.get('translate_references', False)
                    )
                    
                    # Guardar cache actualizado para posible reanudación
                    if result.get('translated_chunks_cache'):
                        if file.name not in st.session_state.translated_chunks_progress:
                            st.session_state.translated_chunks_progress[file.name] = {}
                        st.session_state.translated_chunks_progress[file.name]['chunks_cache'] = result['translated_chunks_cache']
                    
                    # Preparar contenido para exportacion
                    content_to_export = result.get('final_content') or result.get('translated_content')
                    if content_to_export:
                        if isinstance(content_to_export, str):
                            result['export_content'] = content_to_export
                        else:
                            result['export_content'] = str(content_to_export)
                    else:
                        result['export_content'] = result.get('error', 'Error en traduccion')
                    
                    # Asegurar que original_text exista
                    if 'original_text' not in result or not result['original_text']:
                        result['original_text'] = str(result.get('original_content', ''))[:500]
                    
                    st.session_state.results.append(result)
                    
                except Exception as e:
                    st.session_state.results.append({
                        'name': file.name,
                        'extension': os.path.splitext(file.name)[1],
                        'status': 'error',
                        'error': str(e),
                        'export_content': f"Error: {e}",
                        'original_content': '',
                        'original_text': f"Error al leer archivo: {str(e)}",
                        'step_history': []
                    })
                finally:
                    # Limpiar archivo temporal
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                
                # Actualizar progreso al completar archivo
                progress_bar.progress((i + 1) / len(uploaded_files))
                status_text.text(f"Completado: {file.name} ({i+1}/{len(uploaded_files)})")
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            progress_bar.empty()
            status_text.text("✅ Procesamiento completado")
            st.session_state.processing = False
    
    # Mostrar resultados si existen
    if st.session_state.results:
        st.markdown("---")
        st.header("📊 Resultados del Procesamiento")
        
        # Tabla de resultados
        results_data = []
        for result in st.session_state.results:
            steps_completed = len([s for s in result.get('step_history', []) if s.get('status') == 'completado'])
            results_data.append({
                'Archivo': result['name'],
                'Estado': result['status'].upper(),
                'Pasos': f"{steps_completed}/4",
                'Error': result.get('error', 'N/A')[:50] if result.get('error') else 'N/A'
            })
        
        st.dataframe(results_data, width='stretch')
        
        # Detalles de cada archivo
        with st.expander("📝 Ver detalles de traducciones", expanded=False):
            for result in st.session_state.results:
                st.subheader(f"📄 {result['name']}")
                
                # Mostrar historial de pasos
                if result.get('step_history'):
                    st.markdown("**Pasos del Proceso:**")
                    for step in result['step_history']:
                        status_icon = "✅" if step.get('status') == 'completado' else "❌"
                        st.write(f"{status_icon} {step.get('step', 'N/A').upper()} - {step.get('status', 'N/A')}")
                        if step.get('details'):
                            st.json(step['details'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Contenido Original:**")
                    original_text = result.get('original_text', '')
                    if not original_text:
                        # Fallback: extraer de original_content
                        oc = result.get('original_content', '')
                        if isinstance(oc, dict) and 'paragraphs' in oc:
                            original_text = '\n\n'.join([p.get('text', '') for p in oc.get('paragraphs', [])])
                        elif isinstance(oc, str):
                            original_text = oc
                        else:
                            original_text = str(oc) if oc else ''
                    
                    if original_text:
                        st.text_area(
                            "Original",
                            value=original_text[:1000] + "..." if len(original_text) > 1000 else original_text,
                            height=200,
                            disabled=True,
                            key=f"orig_{result['name']}"
                        )
                    else:
                        st.info("Contenido original no disponible")
                
                with col2:
                    st.markdown("**Traduccion:**")
                    translated = result.get('final_content') or result.get('translated_content')
                    if translated:
                        translated_text = translated if isinstance(translated, str) else str(translated)
                        
                        # Verificar si hay errores en la traduccion
                        if '[ERROR' in translated_text:
                            st.error("La traduccion falló. Verifique la consola para detalles.")
                            st.code(translated_text, language=None)
                        else:
                            st.text_area(
                                "Traduccion",
                                value=translated_text[:1000] + "..." if len(translated_text) > 1000 else translated_text,
                                height=200,
                                key=f"trans_{result['name']}"
                            )
                        
                        # Boton de descarga individual
                        export_filename = ZipExporter._get_export_filename(result['name'], result['extension'])
                        
                        # Para PDFs, usar los bytes del PDF generado con maquetación completa
                        if result['extension'].lower() == '.pdf':
                            pdf_data = result.get('pdf_bytes')
                            if not pdf_data:
                                docx_p = result.get('docx_path')
                                out_docx_p = docx_p.replace('.docx', '_traducido.docx') if docx_p else None
                                if out_docx_p and os.path.exists(out_docx_p):
                                    conv_pdf = FileHandlerLocal.docx_to_pdf(out_docx_p)
                                    if conv_pdf and os.path.exists(conv_pdf):
                                        with open(conv_pdf, 'rb') as pf:
                                            pdf_data = pf.read()
                                        result['pdf_bytes'] = pdf_data
                                        result['pdf_path'] = conv_pdf

                            if not pdf_data:
                                try:
                                    tmp_pdf_path = os.path.join(tempfile.gettempdir(), f"tmp_dl_{os.getpid()}_{int(time.time())}.pdf")
                                    if FileHandlerLocal.write_file(tmp_pdf_path, translated_text, result) and os.path.exists(tmp_pdf_path):
                                        with open(tmp_pdf_path, 'rb') as f:
                                            pdf_data = f.read()
                                        result['pdf_bytes'] = pdf_data
                                        try:
                                            os.unlink(tmp_pdf_path)
                                        except Exception:
                                            pass
                                except Exception as e:
                                    print(f"Error generando PDF para descarga: {e}")

                            if pdf_data:
                                st.download_button(
                                    label=f"⬇️ Descargar {export_filename}",
                                    data=pdf_data,
                                    file_name=export_filename,
                                    mime="application/pdf",
                                    key=f"download_{result['name']}"
                                )
                            else:
                                txt_filename = export_filename.replace('.pdf', '.txt')
                                st.download_button(
                                    label=f"⬇️ Descargar {txt_filename}",
                                    data=translated_text,
                                    file_name=txt_filename,
                                    key=f"download_{result['name']}"
                                )
                        else:
                            st.download_button(
                                label=f"⬇️ Descargar {export_filename}",
                                data=translated_text,
                                file_name=export_filename,
                                key=f"download_{result['name']}"
                            )
                
                # Mostrar revision
                if result.get('review'):
                    st.markdown("**Revision de Calidad:**")
                    review = result['review']
                    score = review.get('score', 'N/A')
                    status = review.get('status', 'N/A')
                    
                    # Mostrar con color segun el estado
                    if status == 'RECHAZADO' or (isinstance(score, (int, float)) and score < 50):
                        st.error(f"Puntuacion: {score}/100 - {status}")
                    elif status == 'APROBADO':
                        st.success(f"Puntuacion: {score}/100 - {status}")
                    else:
                        st.metric("Puntuacion", f"{score}/100")
                        st.write(f"**Estado:** {status}")
                    
                    if review.get('summary'):
                        st.info(review['summary'])
                
                # Mostrar extraccion
                if result.get('extraction'):
                    st.markdown("**Analisis del Extractor:**")
                    extraction = result['extraction']
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**Idioma:** {extraction.get('detected_language', 'N/A')}")
                    with col_b:
                        st.write(f"**Dominio:** {extraction.get('domain', 'N/A')}")
                    with col_c:
                        st.write(f"**Tono:** {extraction.get('tone', 'N/A')}")
                
                st.markdown("---")
        
        # Boton de descarga ZIP
        st.header("📥 Descargar Traducciones")
        
        # Nota sobre formatos
        st.info("📝 **Nota:** Los archivos PDF se exportan preservando su maquetación original (2 columnas, tablas, tipografías e imágenes). Los archivos DOCX, XLSX, etc. mantienen su formato original.")
        
        if st.button("📦 Crear Archivo ZIP", type="primary", width='stretch'):
            with st.spinner("Creando archivo ZIP..."):
                # Preparar datos para exportacion
                translated_dict = {}
                original_extensions = {}
                files_info_map = {}
                
                for result in st.session_state.results:
                    if result['status'] in ['completado', 'completado_con_advertencias', 'revision_requerida']:
                        translated_dict[result['name']] = result.get('export_content', '')
                        original_extensions[result['name']] = result['extension']
                        files_info_map[result['name']] = result
                
                if translated_dict:
                    # Crear ZIP
                    zip_path = ZipExporter.create_zip_from_dict(
                        translated_dict, original_extensions, files_info_map=files_info_map
                    )
                    
                    # Leer contenido del ZIP
                    with open(zip_path, 'rb') as f:
                        zip_data = f.read()
                    
                    # Obtener lista de archivos en el ZIP
                    zip_contents = ZipExporter.list_zip_contents(zip_path)
                    
                    # Mostrar archivos que se incluiran
                    st.write("**Archivos que se incluiran en el ZIP:**")
                    for item in zip_contents:
                        st.write(f"  - {item}")
                    
                    # Boton de descarga
                    st.download_button(
                        label="⬇️ Descargar ZIP",
                        data=zip_data,
                        file_name=f"traducciones_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        width='stretch'
                    )
                    
                    st.success(f"✅ Archivo ZIP creado ({ZipExporter.get_zip_size_mb(zip_path):.2f} MB)")
                else:
                    st.warning("⚠️ No hay archivos traducidos para exportar")


if __name__ == "__main__":
    main()
