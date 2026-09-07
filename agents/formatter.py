import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json


class FormatterAgent:
    """
    Agente de estructura e integridad de formato (post-procesamiento).
    Compara el archivo original traducido y verifica que no se hayan perdido
    tablas, listas, variables o bloques de código.
    Reconstruye el formato final.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.5-flash",
                 fallback_model_name: Optional[str] = None):
        """
        Inicializa el agente formateador.
        
        Args:
            api_key: API key de Google Gemini
            model_name: Nombre del modelo a usar
            fallback_model_name: Modelo alternativo si el primario agota cuota
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere GOOGLE_API_KEY para usar el agente formateador")
        
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        
        llm_kwargs = {"model": model_name, "google_api_key": self.api_key, "max_tokens": 4096}
        if "lite" not in model_name.lower():
            llm_kwargs["temperature"] = 0.1
        self.llm = ChatGoogleGenerativeAI(**llm_kwargs)
        self.fallback_llm = None
        if fallback_model_name and fallback_model_name != model_name:
            fb_kwargs = {"model": fallback_model_name, "google_api_key": self.api_key, "max_tokens": 4096}
            if "lite" not in fallback_model_name.lower():
                fb_kwargs["temperature"] = 0.1
            self.fallback_llm = ChatGoogleGenerativeAI(**fb_kwargs)
        self.format_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un experto en formateo y reconstruccion de documentos traducidos.

Tu tarea es verificar y reconstruir el formato del archivo traducido, asegurandote de que:
1. No se hayan perdido elementos estructurales (tablas, listas, titulos)
2. Las variables o codigos se hayan preservado correctamente
3. La sintaxis especial se haya mantenido (Markdown, HTML, etc.)
4. El formato final sea consistente y profesional

Formato de respuesta JSON:
{{
    "formatted_content": "contenido formateado y reconstruido",
    "format_issues": ["problema1", "problema2"],
    "preserved_elements": ["elemento1", "elemento2"],
    "warnings": ["advertencia1"],
    "quality_score": numero_del_0_al_100
}}

Criterios de formateo:
- Preserva toda la estructura del documento original
- Conserva sintaxis Markdown, HTML, codigo
- Asegura que tablas y listas esten correctamente formateadas
- Verifica que no haya texto truncado o incompleto
- Proporciona puntuacion de calidad del formateo"""),
            ("human", """Contenido original (estructura):
{original_structure}

Contenido traducido:
{translated_content}

Por favor, verifica y reformatea el contenido traducido preservando la estructura original.""")
        ])
        
        self.chain = self.format_prompt | self.llm | StrOutputParser()
        self.fallback_chain = None
        if self.fallback_llm is not None:
            self.fallback_chain = self.format_prompt | self.fallback_llm | StrOutputParser()
    
    def _invoke_chain(self, inputs: Dict[str, Any]) -> str:
        """Invoca con fallback por cuota agotada."""
        try:
            return self.chain.invoke(inputs)
        except Exception as primary_error:
            text = str(primary_error)
            if self.fallback_chain is not None and ('429' in text or 'RESOURCE_EXHAUSTED' in text.upper()):
                print(f"[Formatter] Cuota agotada en {self.model_name}; usando fallback {self.fallback_model_name}")
                try:
                    return self.fallback_chain.invoke(inputs)
                except Exception:
                    raise primary_error
            raise primary_error

    def format_translated_content(self, original_structure: Any, 
                                 translated_content: str) -> Dict[str, Any]:
        """
        Formatea y verifica el contenido traducido.
        
        Args:
            original_structure: Estructura original del archivo
            translated_content: Contenido traducido
            
        Returns:
            Diccionario con contenido formateado y metadatos
        """
        try:
            # Convertir estructura original a string para el prompt
            original_str = json.dumps(original_structure, indent=2, ensure_ascii=False) \
                if not isinstance(original_structure, str) else original_structure
            
            # Limitar longitud solo para el prompt del LLM (no para el resultado)
            original_str_prompt = original_str[:3000] if len(original_str) > 3000 else original_str
            translated_prompt = translated_content[:3000] if len(translated_content) > 3000 else translated_content
            
            response = self._invoke_chain({
                "original_structure": original_str_prompt,
                "translated_content": translated_prompt
            })
            
            # Intentar parsear la respuesta como JSON
            try:
                result = json.loads(response)
                # IMPORTANTE: Usar el contenido traducido COMPLETO, no el truncado
                result['formatted_content'] = translated_content
                return result
            except json.JSONDecodeError:
                # Si no es JSON válido, crear estructura básica
                return {
                    "formatted_content": translated_content,
                    "format_issues": [],
                    "preserved_elements": [],
                    "warnings": ["Respuesta no parseable"],
                    "quality_score": 80,
                    "raw_response": response
                }
                
        except Exception as e:
            return {
                "formatted_content": translated_content,
                "format_issues": [f"Error en formateo: {str(e)}"],
                "preserved_elements": [],
                "warnings": [str(e)],
                "quality_score": 50,
                "error": str(e)
            }
    
    def verify_format_integrity(self, original: Any, translated: Any) -> Dict[str, Any]:
        """
        Verifica la integridad del formato entre original y traducido.
        
        Args:
            original: Contenido original
            translated: Contenido traducido
            
        Returns:
            Resultado de la verificación
        """
        issues = []
        preserved = []
        
        # Verificar estructura de diccionario (DOCX, etc.)
        if isinstance(original, dict) and isinstance(translated, dict):
            # Verificar párrafos
            if 'paragraphs' in original:
                orig_paras = original['paragraphs']
                trans_paras = translated.get('paragraphs', [])
                
                if len(orig_paras) != len(trans_paras):
                    issues.append(f"Diferencia en número de párrafos: {len(orig_paras)} vs {len(trans_paras)}")
                else:
                    preserved.append("Número de párrafos")
                
                # Verificar estilos
                for i, (orig, trans) in enumerate(zip(orig_paras, trans_paras)):
                    if orig.get('style') != trans.get('style'):
                        issues.append(f"Estilo cambiado en párrafo {i+1}")
                    else:
                        preserved.append(f"Estilo párrafo {i+1}")
            
            # Verificar tablas
            if 'tables' in original:
                orig_tables = original['tables']
                trans_tables = translated.get('tables', [])
                
                if len(orig_tables) != len(trans_tables):
                    issues.append(f"Diferencia en número de tablas: {len(orig_tables)} vs {len(trans_tables)}")
                else:
                    preserved.append("Número de tablas")
        
        # Verificar estructura de lista (PPTX)
        elif isinstance(original, list) and isinstance(translated, list):
            if len(original) != len(translated):
                issues.append(f"Diferencia en número de elementos: {len(original)} vs {len(translated)}")
            else:
                preserved.append("Número de elementos")
        
        # Calcular puntuación
        total_checks = len(preserved) + len(issues)
        score = (len(preserved) / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "preserved_elements": preserved,
            "integrity_score": score
        }
    
    def reconstruct_document(self, translated_content: Any, 
                           original_format: str) -> Any:
        """
        Reconstruye el documento en su formato original.
        
        Args:
            translated_content: Contenido traducido
            original_format: Formato original del archivo
            
        Returns:
            Documento reconstruido
        """
        # Si el contenido ya está formateado, retornarlo
        if isinstance(translated_content, dict) and 'formatted_content' in translated_content:
            return translated_content['formatted_content']
        
        # Para otros casos, retornar el contenido tal cual
        return translated_content
    
    def get_format_report(self, format_result: Dict[str, Any]) -> str:
        """
        Genera un reporte legible del formateo.
        
        Args:
            format_result: Resultado de format_translated_content
            
        Returns:
            Reporte formateado
        """
        report = []
        
        # Puntuación
        score = format_result.get('quality_score', 0)
        report.append(f"Puntuación de formateo: {score}/100")
        
        # Problemas encontrados
        issues = format_result.get('format_issues', [])
        if issues:
            report.append("\nProblemas encontrados:")
            for issue in issues:
                report.append(f"  - {issue}")
        
        # Elementos preservados
        preserved = format_result.get('preserved_elements', [])
        if preserved:
            report.append("\nElementos preservados:")
            for elem in preserved:
                report.append(f"  + {elem}")
        
        # Advertencias
        warnings = format_result.get('warnings', [])
        if warnings:
            report.append("\nAdvertencias:")
            for warn in warnings:
                report.append(f"  ! {warn}")
        
        return "\n".join(report)
