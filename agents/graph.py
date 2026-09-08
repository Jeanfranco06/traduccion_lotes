import os
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
import json

from agents.extractor import ExtractorAgent
from agents.translator import TranslatorAgent
from agents.reviewer import QualityReviewer
from agents.formatter import FormatterAgent
from utils.file_handlers import FileHandler


class TranslationState(TypedDict):
    """Estado del grafo de traducción."""
    # Datos de entrada
    file_name: str
    file_extension: str
    original_content: Any
    source_language: str
    target_language: str
    
    # Estado del proceso
    current_step: str
    iteration_count: int
    max_iterations: int
    
    # Resultados intermedios
    extraction_result: Optional[Dict[str, Any]]
    normalized_text: Optional[str]
    translation_context: Optional[str]
    translated_content: Optional[str]
    review_result: Optional[Dict[str, Any]]
    format_result: Optional[Dict[str, Any]]
    
    # Resultado final
    final_content: Optional[str]
    status: str
    error: Optional[str]
    
    # Referencias separadas (para mejor formateo PDF)
    references_text: Optional[str]
    
    # Si las referencias deben traducirse o preservarse en el idioma original
    translate_references: bool
    
    # Historial para visualización
    step_history: List[Dict[str, Any]]
    
    # Conversion de PDF
    docx_path: Optional[str]
    is_pdf_conversion: bool
    
    # Cache de chunks traducidos (para reanudación)
    translated_chunks_cache: Optional[List[str]]
    total_chunks: Optional[int]
    last_chunk_index: Optional[int]


class TranslationGraph:
    """
    Grafo de traducción multi-agente usando LangGraph.
    Implementa el flujo: Extractor → Traductor → Revisor → Formateador
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash"):
        """
        Inicializa el grafo de traducción.
        
        Args:
            api_key: API key de Google Gemini
            model_name: Nombre del modelo a usar
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.fallback_model = self._pick_fallback(model_name)
        
        # Inicializar agentes
        self.extractor = ExtractorAgent(api_key=self.api_key, model_name=model_name, fallback_model_name=self.fallback_model)
        self.translator = TranslatorAgent(api_key=self.api_key, model_name=model_name, fallback_model_name=self.fallback_model)
        self.reviewer = QualityReviewer(api_key=self.api_key, model_name=model_name, fallback_model_name=self.fallback_model)
        self.formatter = FormatterAgent(api_key=self.api_key, model_name=model_name, fallback_model_name=self.fallback_model)
        
        # Construir el grafo
        self.graph = self._build_graph()
    
    @staticmethod
    def _pick_fallback(model_name: str) -> Optional[str]:
        """
        Elige un modelo de respaldo cuando el primario agota su cuota.
        flash <-> flash-lite; otros modelos sin fallback configurado.
        """
        if model_name == "gemini-3.5-flash":
            return "gemini-3.5-flash-lite"
        if model_name == "gemini-3.5-flash-lite":
            return "gemini-3.5-flash"
        return None
    
    def _build_graph(self) -> StateGraph:
        """
        Construye el grafo de estados con LangGraph.
        
        Returns:
            Grafo compilado
        """
        # Crear grafo de estados
        workflow = StateGraph(TranslationState)
        
        # Agregar nodos (agentes)
        workflow.add_node("extractor", self._extractor_node)
        workflow.add_node("translator", self._translator_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("formatter", self._formatter_node)
        workflow.add_node("corrector", self._corrector_node)
        
        # Definir punto de entrada
        workflow.set_entry_point("extractor")
        
        # Agregar aristas
        workflow.add_edge("extractor", "translator")
        workflow.add_edge("translator", "reviewer")
        
        # Arista condicional desde el revisor
        workflow.add_conditional_edges(
            "reviewer",
            self._decide_next_step,
            {
                "approve": "formatter",
                "reject": "corrector"
            }
        )
        
        workflow.add_edge("corrector", "reviewer")
        workflow.add_edge("formatter", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def _extractor_node(self, state: TranslationState) -> Dict[str, Any]:
        """
        Nodo extractor: Analiza y normaliza el documento.
        """
        state['current_step'] = 'extractor'
        state['step_history'].append({
            'step': 'extractor',
            'status': 'iniciado',
            'timestamp': self._get_timestamp()
        })
        
        # Reportar progreso
        if hasattr(self, '_progress_callback') and self._progress_callback:
            self._progress_callback('extractor', 0.1)
        
        try:
            # Extraer texto del contenido
            raw_text = self.extractor.extract_text_from_content(state['original_content'])
            
            # Limpiar el texto extraido
            cleaned_text = self.extractor.clean_extracted_text(raw_text)
            
            # Analizar y normalizar (solo para obtener metadata, no el texto)
            analysis = self.extractor.analyze_and_normalize(cleaned_text[:3000] if len(cleaned_text) > 3000 else cleaned_text)
            
            # Preparar contexto para traduccion
            context = self.extractor.prepare_translation_context(
                analysis, 
                state['source_language'], 
                state['target_language']
            )
            
            state['extraction_result'] = analysis
            # Usar el texto limpio original, no el del LLM que puede estar truncado
            state['normalized_text'] = cleaned_text
            state['translation_context'] = context
            
            state['step_history'][-1]['status'] = 'completado'
            state['step_history'][-1]['details'] = {
                'domain': analysis.get('domain'),
                'tone': analysis.get('tone'),
                'detected_language': analysis.get('detected_language')
            }
            
            # Reportar progreso
            if hasattr(self, '_progress_callback') and self._progress_callback:
                self._progress_callback('extractor', 0.25)
            
            # Esperar para evitar rate limiting
            import time
            time.sleep(2)
            
        except Exception as e:
            state['error'] = f"Error en extraccion: {str(e)}"
            state['step_history'][-1]['status'] = 'error'
            state['step_history'][-1]['error'] = str(e)
        
        return state
    
    def _translator_node(self, state: TranslationState) -> Dict[str, Any]:
        """
        nodo traductor: Genera la traduccion del texto.
        """
        state['current_step'] = 'translator'
        state['step_history'].append({
            'step': 'translator',
            'status': 'iniciado',
            'timestamp': self._get_timestamp()
        })
        
        # Reportar progreso
        if hasattr(self, '_progress_callback') and self._progress_callback:
            self._progress_callback('translator', 0.25)
        
        try:
            # Verificar que haya contenido para traducir
            original = state.get('original_content')
            if not original:
                state['translated_content'] = ""
                state['step_history'][-1]['status'] = 'completado'
                state['step_history'][-1]['details'] = {'content_length': 0}
                return state
            
            # Obtener texto plano para traducir
            # Si es PDF y tenemos docx_path, ejecutar traducción estructurada in-place sobre el DOCX
            if state.get('is_pdf_conversion') and state.get('docx_path'):
                from utils.file_handlers import FileHandler
                docx_path = state['docx_path']
                if os.path.exists(docx_path):
                    out_docx = docx_path.replace('.docx', '_traducido.docx')
                    print(f"[Translator] Ejecutando traducción estructurada in-place sobre DOCX: {docx_path}")
                    
                    analysis = state.get('extraction_result') or {}
                    translation_context = state.get('translation_context') or ""
                    glossary = self.translator.build_glossary(
                        analysis, state['source_language'], state['target_language']
                    )
                    
                    def in_place_cb(cur_b, tot_b):
                        if hasattr(self, '_progress_callback') and self._progress_callback:
                            p = 0.25 + (0.35 * (cur_b / tot_b))
                            chunk_info = {'current': cur_b, 'total': tot_b}
                            self._progress_callback('translator', p, chunk_info)

                    success = FileHandler.translate_docx_in_place(
                        docx_path=docx_path,
                        output_docx_path=out_docx,
                        translator_agent=self.translator,
                        source_language=state['source_language'],
                        target_language=state['target_language'],
                        context=translation_context,
                        glossary=glossary,
                        translate_references=state.get('translate_references', False),
                        progress_callback=in_place_cb
                    )
                    
                    # Extraer el texto traducido resultante para el revisor
                    translated_text = FileHandler.extract_text_from_docx(out_docx if success else docx_path)
                    state['translated_content'] = translated_text
                    state['step_history'][-1]['status'] = 'completado'
                    state['step_history'][-1]['details'] = {
                        'content_length': len(translated_text),
                        'structured_docx_translation': success
                    }
                    return state
            
            text_to_translate = state.get('normalized_text')
            if not text_to_translate:
                text_to_translate = self.extractor.extract_text_from_content(original)

            # Limpiar el texto extraido
            text_to_translate = self.extractor.clean_extracted_text(text_to_translate)
            
            # Verificar que el texto no este vacio
            if not text_to_translate or len(text_to_translate.strip()) == 0:
                state['translated_content'] = ""
                state['step_history'][-1]['status'] = 'completado'
                state['step_history'][-1]['details'] = {'content_length': 0}
                return state
            
            print(f"[Translator] Text to translate length: {len(text_to_translate)}")
            print(f"[Translator] Source: {state['source_language']}, Target: {state['target_language']}")
            print(f"[Translator] First 200 chars: {text_to_translate[:200]}")
            
            # Separar referencias del cuerpo del texto.
            # IMPORTANTE: solo se corta ante un ENCABEZADO AISLADO (línea que
            # contiene únicamente "References"/"REFERENCES", etc.). Si se usara
            # la primera aparición de la palabra "references" dentro de una
            # frase, se cortaría el cuerpo a la mitad (p. ej. "All references
            # were organized...").
            import re
            ref_heading = re.search(
                r'(?im)^\s*(REFERENCES|REFERENCIAS|BIBLIOGRAPHY|BIBLIOGRAFÍA)\s*:?\s*$',
                text_to_translate
            )
            if ref_heading:
                split_at = ref_heading.start()
                body_text = text_to_translate[:split_at]
                references_text = text_to_translate[split_at:]
            else:
                # Fallback: si no hay encabezado aislado, intentar la última
                # aparición de la palabra como encabezado (p. ej. "References"
                # pegado a la primera referencia).
                last_hit = None
                for m in re.finditer(r'(?im)(REFERENCES|REFERENCIAS|BIBLIOGRAPHY|BIBLIOGRAFÍA)', text_to_translate):
                    last_hit = m
                if last_hit:
                    body_text = text_to_translate[:last_hit.start()]
                    references_text = text_to_translate[last_hit.start():]
                else:
                    body_text = text_to_translate
                    references_text = ""
            
            # Guardar referencias en estado (para mejor formateo PDF)
            state['references_text'] = references_text.strip() if references_text else None
            
            print(f"[Translator] Body text: {len(body_text)} chars, References: {len(references_text)} chars")

            # Preparar contexto y glosario a partir del análisis del extractor
            analysis = state.get('extraction_result') or {}
            translation_context = state.get('translation_context') or ""
            glossary = self.translator.build_glossary(
                analysis, state['source_language'], state['target_language']
            )
            print(f"[Translator] Context: {len(translation_context)} chars, Glossary terms: {len(glossary) if glossary else 0}")

            # Definir si las referencias deben traducirse (por defecto: NO)
            translate_references = state.get('translate_references', False)
            
            # Dividir el cuerpo en fragmentos
            max_chunk_size = 15000
            chunks = []
            
            if len(body_text) > max_chunk_size:
                # Dividir por párrafos (doble salto de línea)
                paragraphs = body_text.split('\n\n')
                current_chunk = ""
                
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    
                    # Si el párrafo es muy largo, dividir por oraciones
                    if len(para) > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        sentences = re.split(r'(?<=[.!?])\s+', para)
                        for sent in sentences:
                            if len(current_chunk) + len(sent) + 1 > max_chunk_size:
                                if current_chunk:
                                    chunks.append(current_chunk.strip())
                                current_chunk = sent
                            else:
                                current_chunk = current_chunk + " " + sent if current_chunk else sent
                    elif len(current_chunk) + len(para) + 2 > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = para
                    else:
                        current_chunk = current_chunk + "\n\n" + para if current_chunk else para
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks = [body_text]
            
            # Agregar las referencias como último chunk (sin traducir, solo preservar)
            if references_text:
                chunks.append(references_text.strip())
            
            print(f"[Translator] Total chunks to translate: {len(chunks)}")
            
            # Verificar si hay chunks en cache para reanudar
            cached_chunks = state.get('translated_chunks_cache', []) or []
            start_index = len(cached_chunks)
            
            if start_index > 0:
                print(f"[Translator] Reanudando desde chunk {start_index + 1}/{len(chunks)} (cache: {start_index} chunks)")
                translated_chunks = cached_chunks.copy()
            else:
                translated_chunks = []
            
            # Traducir cada fragmento (desde start_index)
            import time
            total_chunks = len(chunks)
            for i in range(start_index, total_chunks):
                chunk = chunks[i]
                try:
                    # Reportar progreso durante traduccion (25% a 60%)
                    if hasattr(self, '_progress_callback') and self._progress_callback:
                        progress = 0.25 + (0.35 * (i / total_chunks))
                        chunk_info = {'current': i + 1, 'total': total_chunks}
                        self._progress_callback('translator', progress, chunk_info)
                    
                    # Esperar entre llamadas para evitar rate limiting
                    if i > start_index:
                        wait_time = 2  # 2 segundos entre llamadas
                        print(f"[Translator] Esperando {wait_time}s antes del chunk {i+1}/{total_chunks}...")
                        time.sleep(wait_time)
                    
                    print(f"[Translator] Traduciendo chunk {i+1}/{total_chunks} ({len(chunk)} chars)...")
                    
                    # Detectar si es el chunk de referencias (último chunk con referencias)
                    is_references = (i == total_chunks - 1 and references_text and 
                                    chunk.strip() == references_text.strip())
                    
                    if is_references:
                        if translate_references:
                            # Traducir las referencias (manteniendo nombres propios/protocolo)
                            translated = self._translate_chunk_with_retries(
                                chunk, state['source_language'], state['target_language'],
                                translation_context, glossary, force=True
                            )
                            translated_chunks.append(translated)
                            print(f"[Translator] Chunk {i+1} referencias traducidas")
                        else:
                            # Preservar referencias tal cual (configuración por defecto)
                            translated_chunks.append(chunk)
                            print(f"[Translator] Chunk {i+1} son referencias - preservado sin traducir")
                    else:
                        # Traducir chunk de cuerpo con contexto + glosario + validación
                        translated = self._translate_chunk_with_retries(
                            chunk, state['source_language'], state['target_language'],
                            translation_context, glossary, force=False
                        )
                        translated_chunks.append(translated)
                    
                    # Guardar progreso parcial en el estado
                    state['translated_chunks_cache'] = translated_chunks.copy()
                    state['last_chunk_index'] = i
                    
                except Exception as e:
                    # Si es el chunk de referencias, no reintentar traducción
                    if is_references:
                        translated_chunks.append(chunk)
                        print(f"[Translator] Chunk {i+1} referencias preservadas (error ignorado)")
                    else:
                        error_msg = str(e)
                        if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                            print(f"[Translator] Rate limit alcanzado, esperando 30s...")
                            time.sleep(30)
                            # Reintentar una vez
                            try:
                                translated = self._translate_chunk_with_retries(
                                    chunk, state['source_language'], state['target_language'],
                                    translation_context, glossary, force=True
                                )
                                translated_chunks.append(translated)
                                state['translated_chunks_cache'] = translated_chunks.copy()
                                state['last_chunk_index'] = i
                            except Exception as retry_e:
                                print(f"[Translator] Error en reintento chunk {i+1}: {str(retry_e)[:100]}")
                                translated_chunks.append(f"[ERROR: {str(retry_e)[:50]}]")
                                state['translated_chunks_cache'] = translated_chunks.copy()
                                state['last_chunk_index'] = i
                        else:
                            print(f"[Translator] Error traduciendo chunk {i+1}: {str(e)[:100]}")
                            translated_chunks.append(f"[ERROR: {str(e)[:50]}]")
                            state['translated_chunks_cache'] = translated_chunks.copy()
                            state['last_chunk_index'] = i
            
            # Unir todos los fragmentos traducidos con doble salto para separar párrafos
            state['translated_content'] = '\n\n'.join(translated_chunks)
            
            state['step_history'][-1]['status'] = 'completado'
            state['step_history'][-1]['details'] = {
                'content_length': len(state['translated_content']),
                'chunks_translated': len(chunks)
            }
            
        except Exception as e:
            # En caso de error critico, reportar en vez de usar fallback
            error_msg = f"Error critico en traduccion: {str(e)}"
            print(f"[Translator] {error_msg}")
            state['translated_content'] = f"[ERROR CRITICO: {error_msg}]"
            state['error'] = error_msg
            
            state['step_history'][-1]['status'] = 'error'
            state['step_history'][-1]['details'] = {'error': str(e)}
        
        return state
    
    def _reviewer_node(self, state: TranslationState) -> Dict[str, Any]:
        """
        Nodo revisor: Evalua la calidad de la traduccion.
        """
        state['current_step'] = 'reviewer'
        state['step_history'].append({
            'step': 'reviewer',
            'status': 'iniciado',
            'timestamp': self._get_timestamp()
        })
        
        # Reportar progreso
        if hasattr(self, '_progress_callback') and self._progress_callback:
            self._progress_callback('reviewer', 0.6)
        
        # Esperar para evitar rate limiting
        import time
        time.sleep(2)
        
        try:
            # Obtener texto original para comparar (usar DOCX si viene de PDF para mantener la misma estructura del traductor)
            if state.get('is_pdf_conversion') and state.get('docx_path') and os.path.exists(state['docx_path']):
                original_text = FileHandler.extract_text_from_docx(state['docx_path'])
            elif state.get('normalized_text'):
                original_text = state['normalized_text']
            else:
                original_text = self.extractor.extract_text_from_content(state['original_content'])
            
            original_text = self.extractor.clean_extracted_text(original_text)
            
            # Verificar que haya contenido traducido
            translated_text = state.get('translated_content', '')
            
            # Excluir las referencias de la comparación si se preservaron en el
            # idioma original (evita falsas alarmas de "texto sin traducir").
            refs = state.get('references_text')
            if refs and translated_text and refs in translated_text:
                translated_text = translated_text.replace(refs, '').strip()
            if refs and original_text and refs in original_text:
                original_text = original_text.replace(refs, '').strip()
            
            # Si hay errores en la traduccion, reportarlos directamente
            if not translated_text or '[ERROR' in translated_text:
                state['review_result'] = {
                    'score': 0,
                    'status': 'RECHAZADO',
                    'errors': [{
                        'type': 'traduccion_fallida',
                        'description': 'La traduccion fallo. El contenido no fue traducido.',
                        'suggestion': 'Verifique la API key y la cuota disponible.'
                    }],
                    'summary': 'Traduccion fallida - usar el modo de depuracion para ver errores.'
                }
                state['step_history'][-1]['status'] = 'completado'
                state['step_history'][-1]['details'] = {'score': 0, 'status': 'RECHAZADO'}
                return state
            
            # Revisar traduccion (el reviewer divide en secciones internamente,
            # y aplica comprobación léxica de idioma sobre el texto completo)
            review = self.reviewer.review_translation(
                original_text if original_text else "",
                translated_text if translated_text else "",
                state['source_language'],
                state['target_language']
            )
            
            state['review_result'] = review
            state['step_history'][-1]['status'] = 'completado'
            state['step_history'][-1]['details'] = {
                'score': review.get('score', 0),
                'status': review.get('status', 'UNKNOWN')
            }
            
        except Exception as e:
            state['error'] = f"Error en revisión: {str(e)}"
            state['step_history'][-1]['status'] = 'error'
            state['step_history'][-1]['error'] = str(e)
        
        return state
    
    def _corrector_node(self, state: TranslationState) -> Dict[str, Any]:
        """
        Nodo corrector: Corrige la traducción basado en feedback del revisor.
        """
        state['current_step'] = 'corrector'
        state['iteration_count'] += 1
        state['step_history'].append({
            'step': 'corrector',
            'status': 'iniciado',
            'timestamp': self._get_timestamp(),
            'iteration': state['iteration_count']
        })
        
        try:
            # Obtener sugerencias del revisor
            review = state.get('review_result', {})
            errors = review.get('errors', [])
            
            if not errors:
                # No hay errores que corregir
                state['translated_content'] = state.get('translated_content', "")
                state['step_history'][-1]['status'] = 'completado'
                state['step_history'][-1]['details'] = {'corrections_applied': 0}
                return state
            
            # Crear prompt de corrección DEDICADO (no el de traducción),
            # pidiendo reescribir SOLO los errores detectados.
            correction_prompt = (
                f"Eres un revisor experto de traducciones. Corrige la siguiente traducción "
                f"que está en {state['target_language']}, aplicando SOLO estas correcciones:\n\n"
                + json.dumps(errors, indent=2, ensure_ascii=False)
                + "\n\nTraducción actual:\n"
                + state['translated_content']
                + "\n\nInstrucciones:\n"
                + "1. Reescribe la traducción completa corrigiendo ÚNICAMENTE los errores listados.\n"
                + f"2. El texto final DEBE estar completamente en {state['target_language']}, sin mezclar con {state['source_language']}.\n"
                + "3. No añadas notas, ni explicaciones, ni metadatos. Devuelve solo la traducción corregida."
            )
            
            # Usar el LLM directamente con la instrucción de corrección,
            # a través de un ChatPromptTemplate mínimo de corrección.
            from langchain_core.prompts import ChatPromptTemplate
            correction_chain = ChatPromptTemplate.from_messages([
                ("human", "{prompt}")
            ]) | self.translator.llm | StrOutputParser()
            # Construir cadena de respaldo con el modelo fallback del traductor
            if self.translator.fallback_llm is not None:
                fallback_correction_chain = ChatPromptTemplate.from_messages([
                    ("human", "{prompt}")
                ]) | self.translator.fallback_llm | StrOutputParser()
            else:
                fallback_correction_chain = None
            
            try:
                corrected = str(correction_chain.invoke({"prompt": correction_prompt}) or "").strip()
            except Exception as corr_err:
                err_text = str(corr_err)
                if fallback_correction_chain is not None and ('429' in err_text or 'RESOURCE_EXHAUSTED' in err_text.upper()):
                    print(f"[Corrector] Cuota agotada en {self.model_name}; usando fallback {self.translator.fallback_model_name}")
                    corrected = str(fallback_correction_chain.invoke({"prompt": correction_prompt}) or "").strip()
                else:
                    raise corr_err
            
            # Si la corrección quedó vacía o idénticamente igual, conservar la anterior
            if (not corrected or corrected.lower() == state['translated_content'].lower()):
                corrected = state.get('translated_content', "")
            
            # Validación de idioma: si la corrección quedó en idioma origen,
            # conservar la traducción anterior (mejor que empeorar).
            if TranslatorAgent.looks_untranslated(corrected, state['source_language'], state['target_language']):
                print("[Corrector] Salida del modelo en idioma origen; conservando traducción anterior")
                corrected = state.get('translated_content', "")
            
            state['translated_content'] = corrected
            state['step_history'][-1]['status'] = 'completado'
            state['step_history'][-1]['details'] = {
                'corrections_applied': len(errors)
            }
            
        except Exception as e:
            state['error'] = f"Error en corrección: {str(e)}"
            state['step_history'][-1]['status'] = 'error'
            state['step_history'][-1]['error'] = str(e)
        
        return state
    
    def _formatter_node(self, state: TranslationState) -> Dict[str, Any]:
        """
        nodo formateador: Reconstruye el formato final del documento.
        """
        state['current_step'] = 'formatter'
        state['step_history'].append({
            'step': 'formatter',
            'status': 'iniciado',
            'timestamp': self._get_timestamp()
        })
        
        # Reportar progreso
        if hasattr(self, '_progress_callback') and self._progress_callback:
            self._progress_callback('formatter', 0.8)
        
        # Esperar para evitar rate limiting
        import time
        time.sleep(2)
        
        try:
            # Para archivos de texto simple, usar el contenido traducido directamente
            # (el formatter con LLM puede perder los saltos de linea)
            file_ext = state.get('file_extension', '').lower()
            
            if file_ext in ['.txt', '.pdf', '.docx']:
                # Para texto plano, PDF y DOCX: usar traduccion directa
                state['final_content'] = state['translated_content']
                state['format_result'] = {
                    'formatted_content': state['translated_content'],
                    'quality_score': 90,
                    'format_issues': [],
                    'preserved_elements': ['saltos de linea', 'estructura basica']
                }
            else:
                # Para otros formatos (JSON, HTML, etc): usar formatter con LLM
                format_result = self.formatter.format_translated_content(
                    state['original_content'],
                    state['translated_content']
                )
                
                final_content = self.formatter.reconstruct_document(
                    format_result,
                    state['file_extension']
                )
                
                state['format_result'] = format_result
                state['final_content'] = final_content if isinstance(final_content, str) else state['translated_content']
            
            state['status'] = 'completado'
            
            state['step_history'][-1]['status'] = 'completado'
            state['step_history'][-1]['details'] = {
                'quality_score': state.get('format_result', {}).get('quality_score', 90)
            }
            
        except Exception as e:
            state['error'] = f"Error en formateo: {str(e)}"
            state['final_content'] = state['translated_content']
            state['status'] = 'completado_con_advertencias'
            state['step_history'][-1]['status'] = 'error'
            state['step_history'][-1]['error'] = str(e)
        
        return state
    
    def _decide_next_step(self, state: TranslationState) -> str:
        """
        Decide si aprobar o rechazar la traducción.
        """
        # Verificar si hay error
        if state.get('error'):
            return "approve"  # Aprobar con error para no bloquear
        
        # Verificar iteración máxima
        if state['iteration_count'] >= state['max_iterations']:
            return "approve"
        
        # Verificar puntuación del revisor
        review = state.get('review_result', {})
        score = review.get('score', 0)
        
        # Si la puntuación es >= 70, aprobar
        if score >= 70:
            return "approve"
        
        # Si hay errores críticos, rechazar para corrección
        errors = review.get('errors', [])
        critical_errors = [e for e in errors if e.get('type') in ['gramatical', 'contexto', 'consistencia']]
        
        if critical_errors and state['iteration_count'] < state['max_iterations']:
            return "reject"
        
        return "approve"
    
    def _translate_chunk_with_retries(self, chunk: str, source_lang: str,
                                      target_lang: str, context: str,
                                      glossary, force: bool = False,
                                      max_attempts: int = 3) -> str:
        """
        Traduce un chunk con contexto y glosario, validando que realmente
        quedó en el idioma destino y reintentando con backoff si falla.

        Args:
            chunk: Texto a traducir
            source_lang: Código del idioma origen
            target_lang: Código del idioma destino
            context: Contexto del documento
            glossary: Glosario de términos (o None)
            force: Si True (referencias), se reintenta con más empeño
            max_attempts: Máximo de intentos

        Returns:
            Traducción del chunk, o marcador [ERROR] si no fue posible
        """
        import time
        if not chunk.strip():
            return ""

        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                out = self.translator.translate_text(
                    text=chunk,
                    source_language=source_lang,
                    target_language=target_lang,
                    context=context,
                    glossary=glossary,
                )
                out = str(out or "").strip()

                if not out:
                    last_error = "respuesta vacía"
                    print(f"[Translator] Intento {attempt}: respuesta vacía para chunk")
                    if attempt < max_attempts:
                        time.sleep(2 * attempt)
                        continue
                    else:
                        return "[ERROR: Traduccion vacia]"

                # Verificar que efectivamente no quede texto del idioma origen
                if TranslatorAgent.looks_untranslated(out, source_lang, target_lang) or \
                   out.lower() == chunk.lower():
                    last_error = "texto no traducido"
                    print(f"[Translator] Intento {attempt}: texto no traducido detectado (len={len(out)})")
                    if attempt < max_attempts:
                        time.sleep(2 * attempt)
                        continue
                    else:
                        return "[ERROR: Traduccion fallida]"
                else:
                    print(f"[Translator] Chunk traducido OK (intento {attempt}, len={len(out)})")
                    return out
            except Exception as e:
                err_text = str(e)
                last_error = err_text
                is_rate_limit = ('429' in err_text) or ('RESOURCE_EXHAUSTED' in err_text)
                # Backoff: ante limitación de cuota esperar más que en errores puntuales
                wait = (15 if is_rate_limit else 3) * attempt
                print(f"[Translator] Error intento {attempt}: {err_text[:90]}. Esperando {wait}s...")
                if attempt < max_attempts:
                    time.sleep(wait)
                    continue
                else:
                    # Tras el último intento, si era por cuota, no marcar el
                    # chunk como "traducido con error" sino devolver el error
                    return f"[ERROR: {err_text[:50]}]"

        return f"[ERROR: {str(last_error)[:50]}]"
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp actual."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def translate_document(self, file_name: str, file_extension: str,
                          original_content: Any, source_language: str,
                          target_language: str, max_iterations: int = 1,
                          progress_callback=None, docx_path: str = None,
                          translated_chunks_cache: List[str] = None,
                          translate_references: bool = False) -> Dict[str, Any]:
        """
        Traduce un documento completo usando el grafo de agentes.
        
        Args:
            file_name: Nombre del archivo
            file_extension: Extensión del archivo
            original_content: Contenido original del archivo
            source_language: Idioma origen
            target_language: Idioma destino
            max_iterations: Máximo de ciclos de revisión
            progress_callback: Funcion callback para reportar progreso (step_name, progress_float)
            docx_path: Ruta al archivo DOCX si se convirtio desde PDF
            translated_chunks_cache: Chunks ya traducidos previamente (para reanudar)
            translate_references: Si True, traduce también las referencias bibliográficas
            
        Returns:
            Resultado de la traducción
        """
        # Almacenar callback para uso en nodos
        self._progress_callback = progress_callback
        
        # Detectar si es PDF y convertir a DOCX si es necesario
        is_pdf_conversion = False
        
        # Si se proporciono docx_path, usarlo directamente
        if docx_path and os.path.exists(docx_path):
            is_pdf_conversion = True
        elif file_extension.lower() == '.pdf':
            try:
                # Si original_content es una ruta de archivo
                if isinstance(original_content, str) and os.path.exists(original_content):
                    docx_path = FileHandler.pdf_to_docx(original_content)
                    if docx_path:
                        is_pdf_conversion = True
                # Si original_content es bytes
                elif isinstance(original_content, bytes):
                    # Guardar temporalmente el PDF
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                        tmp.write(original_content)
                        tmp_pdf_path = tmp.name
                    
                    docx_path = FileHandler.pdf_to_docx(tmp_pdf_path)
                    if docx_path:
                        is_pdf_conversion = True
                    
                    # Limpiar archivo temporal
                    try:
                        os.unlink(tmp_pdf_path)
                    except:
                        pass
            except Exception as e:
                print(f"Error al convertir PDF a DOCX: {e}")
                # Continuar con el PDF original si falla la conversion
        
        # Estado inicial
        initial_state: TranslationState = {
            'file_name': file_name,
            'file_extension': file_extension,
            'original_content': original_content,
            'source_language': source_language,
            'target_language': target_language,
            'current_step': 'inicio',
            'iteration_count': 0,
            'max_iterations': max_iterations,
            'extraction_result': None,
            'normalized_text': None,
            'translation_context': None,
            'translated_content': None,
            'review_result': None,
            'format_result': None,
            'final_content': None,
            'status': 'procesando',
            'error': None,
            'step_history': [],
            'references_text': None,
            'translate_references': translate_references,
            'docx_path': docx_path,
            'is_pdf_conversion': is_pdf_conversion,
            'translated_chunks_cache': translated_chunks_cache or [],
            'total_chunks': None,
            'last_chunk_index': None
        }
        
        # Ejecutar grafo
        result = self.graph.invoke(initial_state)
        
        return result
    
    def get_graph_visualization(self) -> str:
        """
        Retorna representación visual del grafo para Streamlit.
        
        Returns:
            ASCII art del grafo
        """
        return """
┌─────────────────┐
│   DOCUMENTO     │
│    SUBIDO       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  1. EXTRACTOR   │ ──> Detecta idioma, dominio, normaliza
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. TRADUCTOR   │ ──> Genera traducción preservando formato
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. REVISOR/QA  │ ──> Evalúa precisión, formato y estilo
└────────┬────────┘
         │
   ¿Aprobado?
   ├── NO ──> [Corrección] ──> (vuelve a Revisor)
   └── SÍ
         │
         ▼
┌─────────────────┐
│  4. FORMATEADOR │ ──> Reconstruye formato y empaqueta
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ARCHIVO FINAL   │
│  TRADUCIDO      │
└─────────────────┘
"""
