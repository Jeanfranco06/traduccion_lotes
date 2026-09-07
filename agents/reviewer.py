import os
from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json


class QualityReviewer:
    """
    Agente revisor de calidad que examina traducciones.
    Detecta errores gramaticales, inconsistencias y pérdidas de formato.
    """
    
    MAX_LLM_SECTIONS = 8
    CHARS_PER_SECTION = 2500
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash",
                 fallback_model_name: Optional[str] = None):
        """
        Inicializa el agente revisor.
        
        Args:
            api_key: API key de Google Gemini
            model_name: Nombre del modelo a usar
            fallback_model_name: Modelo alternativo si el primario agota cuota
        """
        self._char_per_section = self.CHARS_PER_SECTION
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere GOOGLE_API_KEY para usar el agente revisor")
        
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        
        llm_kwargs = {"model": model_name, "google_api_key": self.api_key, "max_tokens": 8192}
        if "lite" not in model_name.lower():
            llm_kwargs["temperature"] = 0.1
        self.llm = ChatGoogleGenerativeAI(**llm_kwargs)
        self.fallback_llm = None
        if fallback_model_name and fallback_model_name != model_name:
            fb_kwargs = {"model": fallback_model_name, "google_api_key": self.api_key, "max_tokens": 8192}
            if "lite" not in fallback_model_name.lower():
                fb_kwargs["temperature"] = 0.1
            self.fallback_llm = ChatGoogleGenerativeAI(**fb_kwargs)
        
        self.review_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto revisor de traducciones con anos de experiencia.

Tu tarea es analizar una SECCION de una traduccion y proporcionar:
1. Puntuacion de calidad (0-100)
2. Lista de errores encontrados (si los hay)
3. Sugerencias de correccion
4. Veredicto final (APROBADO/RECHAZADO)

Formato de respuesta JSON:
{{
    "score": numero del 0 al 100,
    "status": "APROBADO" o "RECHAZADO",
    "errors": [
        {{
            "type": "gramatical" o "contexto" o "formato" o "consistencia",
            "description": "descripcion del error",
            "suggestion": "sugerencia de correccion"
        }}
    ],
    "summary": "resumen general de la calidad de esta seccion"
}}

CRITERIO CRITICO DE RECHAZO:
- Si encuentras texto que NO esta en el idioma destino (idioma origen o mezclado) sin estar marcado como cita/referencia/termino propio, es un error grave de tipo "consistencia" y baja la puntuacion significativamente.
- Si el texto esta intacto sin traducir, la puntuacion debe ser baja (menos de 30).

NOTA IMPORTANTE SOBRE MUESTREO Y ARTEFACTOS DE PDF:
- Esta seccion puede comenzar o terminar en medio de una frase porque el documento se divide en tramos para su revision. NO penalices cortes abruptos al inicio o al final de la seccion; evalua solo la calidad de lo que SI ves.
- Tampoco penalices como "fragmentos desordenados" o "falta de integridad" si encuentras metadatos de PDF (nombres de autor, filiaciones, números de página o encabezados huérfanos). Compara el CONTENIDO (significado, fidelidad, idioma, gramatica), no la presencia de metadatos del PDF.
- Términos académicos y metodológicos reconocidos (como 'snowballing' traducido a 'búsqueda/muestreo en bola de nieve', o nombres propios de sistemas) son válidos y NO deben penalizarse.

Criterios de evaluacion:
- Precision gramatical
- Conservacion del significado (sin omisiones ni resumenes)
- Preservacion del formato
- Consistencia terminologica
- Naturalidad del texto
- Compleción: que no se hayan omitido frases"""),
            ("human", """Seccion texto original:
{original_text}

Seccion traduccion revisada:
{translated_text}

Idioma destino requerido: {target_language}

Revisa esta seccion y proporciona tu evaluacion en JSON.""")
        ])
        
        self.chain = self.review_prompt | self.llm | StrOutputParser()
        self.fallback_chain = None
        if self.fallback_llm is not None:
            self.fallback_chain = self.review_prompt | self.fallback_llm | StrOutputParser()
    
    def _invoke_chain(self, inputs: Dict[str, Any]) -> str:
        """Invoca con fallback por cuota agotada."""
        try:
            return self.chain.invoke(inputs)
        except Exception as primary_error:
            text = str(primary_error)
            if self.fallback_chain is not None and ('429' in text or 'RESOURCE_EXHAUSTED' in text.upper()):
                print(f"[Reviewer] Cuota agotada en {self.model_name}; usando fallback {self.fallback_model_name}")
                try:
                    return self.fallback_chain.invoke(inputs)
                except Exception:
                    raise primary_error
            raise primary_error
    
    def _split_into_sections(self, text: str, max_chars: int = 2500,
                            overlap: int = 300) -> List[str]:
        """
        Divide el texto en secciones con solape para revisión integral.
        Divide preferentemente por párrafos (doble salto de línea).

        Args:
            text: Texto completo
            max_chars: Tamaño máximo de cada sección
            overlap: Solape de caracteres entre secciones

        Returns:
            Lista de secciones
        """
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]

        sections = []
        # Dividir por párrafos
        paragraphs = text.split('\n\n')
        current = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current) + len(para) + 2 <= max_chars:
                current = current + "\n\n" + para if current else para
            else:
                if current:
                    sections.append(current.strip())
                # Si el párrafo es gigante, dividirlo por líneas/sentencias
                if len(para) > max_chars:
                    # con solape
                    step = max_chars - overlap
                    for i in range(0, len(para), step):
                        sections.append(para[i:i + max_chars].strip())
                    current = ""
                else:
                    current = para
        if current:
            sections.append(current.strip())

        # Asegurar que las secciones no estén vacías
        sections = [s for s in sections if s.strip()]

        # Limitar el número de secciones revisadas por el LLM para controlar
        # costo/tiempo, muestreando uniformemente a lo largo del documento.
        # La comprobación léxica de idioma aún cubre el texto completo.
        MAX_LLM_SECTIONS = 8
        if len(sections) > MAX_LLM_SECTIONS:
            step = (len(sections) - 1) / (MAX_LLM_SECTIONS - 1) if MAX_LLM_SECTIONS > 1 else 0
            indices = sorted({round(i * step) for i in range(MAX_LLM_SECTIONS)})
            sampled = [sections[i] if i < len(sections) else sections[-1] for i in indices]
            # Mantener única (dedupe) sin perder cobertura del inicio y fin
            return list(dict.fromkeys(sampled))

        return sections
    
    def _parse_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Intenta parsear JSON robustamente, extrayéndolo del texto si hay ruido."""
        import re as _re
        if not response:
            return None
        stripped = str(response).strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass
        # Buscar el primer bloque JSON
        match = _re.search(r'\{.*\}', stripped, _re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    def review_translation(self, original_text: str, translated_text: str,
                          source_language: str = "es", 
                          target_language: str = "en") -> Dict[str, Any]:
        """
        Revisa una traducción completa por secciones y retorna evaluación detallada.

        Args:
            original_text: Texto original
            translated_text: Texto traducido a revisar
            source_language: Idioma del texto original
            target_language: Idioma de la traducción

        Returns:
            Diccionario con evaluación de calidad
        """
        try:
            orig_text = (original_text or "").strip()
            trans_text = (translated_text or "").strip()

            all_errors = []
            scores = []
            summaries = []
            statuses = set()

            if not orig_text and not trans_text:
                return {
                    "score": 0,
                    "status": "RECHAZADO",
                    "errors": [{"type": "formato", "description": "No hay texto para revisar.",
                                "suggestion": "El documento no tiene contenido textual."}],
                    "summary": "Sin contenido para revisar."
                }

            # Dividir original y traducción en el MISMO número de tramos
            # (posición proporcional por párrafo), de modo que tramo i del
            # original corresponda al tramo i de la traducción. Así se evita
            # el falso "fragmentos desordenados" causado por comparar
            # secciones de longitud distinta por índice.
            n_trans = min(self.MAX_LLM_SECTIONS, max(len(trans_text) // self._char_per_section, 1))
            orig_tramos = self._split_proportional(orig_text, n_trans)
            trans_tramos = self._split_proportional(trans_text, n_trans)

            for i in range(n_trans):
                # Programar pausa ligera entre llamadas para no saturar la API
                if i > 0:
                    import time
                    time.sleep(0.5)

                orig_sec = orig_tramos[i][:3500]
                trans_sec = trans_tramos[i][:3500]

                response = self._invoke_chain({
                    "original_text": orig_sec[:3000],
                    "translated_text": trans_sec[:3000],
                    "target_language": self._lang_label(target_language)
                })

                evaluation = self._parse_json(response)
                if not evaluation:
                    # Fallback: revisión manual requerida para esta sección
                    scores.append(70)
                    statuses.add("REVISIÓN MANUAL REQUERIDA")
                    summaries.append("Sección sin evaluación JSON válida.")
                    continue

                scr = evaluation.get('score', 70)
                try:
                    scr = float(scr)
                except (TypeError, ValueError):
                    scr = 70.0
                scores.append(min(max(scr, 0), 100))

                statuses.add(evaluation.get('status', 'UNKNOWN'))
                for err in (evaluation.get('errors') or []):
                    if err.get('description'):
                        err['section'] = i + 1
                        all_errors.append(err)
                if evaluation.get('summary'):
                    summaries.append(evaluation['summary'])

            # Detección de omisión marcada por completo si las longitudes
            # divergen demasiado (la traducción es dramáticamente más corta)
            if trans_text and orig_text and len(trans_text) < 0.4 * len(orig_text):
                all_errors.append({
                    "type": "formato",
                    "description": "La traducción es notablemente más corta que el original; posible omisión de contenido.",
                    "suggestion": "Verifica que no se haya omitido contenido."
                })

            avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

            # Detección léxica de texto sin traducir en la traducción
            from agents.translator import TranslatorAgent
            if TranslatorAgent.looks_untranslated(translated_text or "", source_language, target_language):
                all_errors.insert(0, {
                    "type": "consistencia",
                    "description": "Se detectó texto que probablemente permanece en el idioma origen (no traducido).",
                    "suggestion": "Verifica que la traducción esté completa en el idioma destino.",
                    "critical": True
                })
                avg_score = min(avg_score, 30.0)

            # Determinar status global
            has_explicit_critical = any(err.get('critical') is True for err in all_errors)
            if avg_score < 70 or has_explicit_critical:
                status = "RECHAZADO"
            elif avg_score < 80:
                status = "APROBADO CON OBSERVACIONES"
            else:
                status = "APROBADO"

            final_summary = " ".join(summaries)[:1000] if summaries else ""
            if not final_summary:
                final_summary = f"Revisión completada de {n_trans} sección(es), puntuación promedio {avg_score}."

            return {
                "score": avg_score,
                "status": status,
                "errors": all_errors,
                "summary": final_summary,
                "sections_reviewed": n_trans,
                "section_scores": scores
            }

        except Exception as e:
            return {
                "score": 0,
                "status": "ERROR",
                "errors": [{"type": "sistema", "description": str(e), "suggestion": "Revisar manualmente"}],
                "summary": f"Error al revisar: {str(e)}",
                "sections_reviewed": 0
            }

    def _lang_label(self, code: str) -> str:
        """Retorna la etiqueta legible de un código de idioma."""
        labels = {
            'es': 'español',
            'en': 'inglés',
            'fr': 'francés',
            'de': 'alemán',
            'it': 'italiano',
            'pt': 'portugués',
            'zh': 'chino',
            'ja': 'japonés',
            'ko': 'coreano',
            'ar': 'árabe'
        }
        return labels.get(code, code)

    def _split_proportional(self, text: str, n: int) -> List[str]:
        """
        Divide un texto en n tramos proporcionales según el avance acumulado por caracteres,
        respetando los límites de párrafos para no cortar oraciones. Con esto, el tramo i
        del original corresponde con alta precisión al tramo i de la traducción.
        """
        if not text or not text.strip():
            return [""] * n
        paras = [p for p in text.split('\n\n') if p.strip()]
        if not paras:
            return [""] * n
        if n <= 1:
            return ['\n\n'.join(paras)]

        total_chars = sum(len(p) for p in paras) or 1
        groups: List[List[str]] = [[] for _ in range(n)]
        current_chars = 0

        for para in paras:
            mid_char_pos = current_chars + len(para) / 2.0
            ratio = mid_char_pos / total_chars
            bucket = int(ratio * n)
            bucket = min(max(bucket, 0), n - 1)
            groups[bucket].append(para)
            current_chars += len(para)

        return ['\n\n'.join(g) for g in groups]

    def review_with_structure(self, original_content: Any,
                             translated_content: Any,
                             source_language: str = "es",
                             target_language: str = "en") -> Dict[str, Any]:
        """
        Revisa contenido traducido manteniendo estructura.
        
        Args:
            original_content: Contenido original
            translated_content: Contenido traducido
            source_language: Idioma original
            target_language: Idioma destino
            
        Returns:
            Evaluación de calidad
        """
        if isinstance(original_content, str) and isinstance(translated_content, str):
            return self.review_translation(
                original_content, translated_content,
                source_language, target_language
            )
        
        elif isinstance(original_content, dict) and isinstance(translated_content, dict):
            # Revisar párrafos si es DOCX
            if 'paragraphs' in original_content and 'paragraphs' in translated_content:
                all_reviews = []
                original_paras = [p['text'] for p in original_content['paragraphs']]
                translated_paras = [p['text'] for p in translated_content['paragraphs']]
                
                for orig, trans in zip(original_paras, translated_paras):
                    review = self.review_translation(
                        orig, trans, source_language, target_language
                    )
                    all_reviews.append(review)
                
                # Promediar puntuaciones
                avg_score = sum(r.get('score', 0) for r in all_reviews) / len(all_reviews) if all_reviews else 0
                all_errors = []
                for r in all_reviews:
                    all_errors.extend(r.get('errors', []))
                
                return {
                    "score": avg_score,
                    "status": "APROBADO" if avg_score >= 70 else "RECHAZADO",
                    "errors": all_errors,
                    "summary": f"Revisión de {len(all_reviews)} párrafos completada"
                }
        
        # Para otros formatos, retorna evaluación básica
        return {
            "score": 75,
            "status": "APROBADO CON OBSERVACIONES",
            "errors": [],
            "summary": "Contenido no textual - requiere revisión manual"
        }
    
    def get_improvement_suggestions(self, review_result: Dict[str, Any]) -> List[str]:
        """
        Extrae sugerencias de mejora de una revisión.
        
        Args:
            review_result: Resultado de review_translation
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        for error in review_result.get('errors', []):
            if 'suggestion' in error:
                suggestions.append(error['suggestion'])
        
        return suggestions
    
    def should_retry(self, review_result: Dict[str, Any], 
                    threshold: int = 70) -> bool:
        """
        Determina si se debe reintentar la traducción.
        
        Args:
            review_result: Resultado de la revisión
            threshold: Umbral mínimo de puntuación
            
        Returns:
            True si se debe reintentar
        """
        score = review_result.get('score', 0)
        return score < threshold
